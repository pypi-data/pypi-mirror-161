"""
Generates and submits HTCondor jobs for rapidPE and RIFT
"""

__author__ = "Caitlin Rose, Vinaya Valsan, Daniel Wysocki, Sinead Walsh"

import sys
import os
import json
import logging
import warnings

import datetime
import time
import glob
import h5py
import numpy as np
import lal
from rapid_pe import lalsimutils
from argparse import ArgumentParser
from ligo.gracedb.rest import GraceDb, HTTPError
from rapidpe_rift_pipe.modules import (
    check_switch_m1m2s1s2,
    convert_injections_txt_to_objects,
    run_cmd,
    construct_event_time_string,
    convert_list_string_to_dict,
    transform_s1zs2z_chi,
)
from ligo.lw import ligolw
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils
from rapidpe_rift_pipe.config import Config
from sklearn.neighbors import BallTree


@lsctables.use_in
class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass


_allowed_pipelines = ["gstlal", "spiir", "MBTAOnline"]


def make_parser():
    parser = ArgumentParser()

    parser.add_argument(
        "config",
        help="Configuration file.",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )

    return parser


def main():
    cli_parser = make_parser()
    cli_args = cli_parser.parse_args()

    if cli_args.verbose:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level)

    cfgname = os.path.abspath(cli_args.config)
    config = Config.load(cfgname)

    # TODO: make this a configuration option
    init_directory = os.getcwd()
    output_parent_directory = config.output_parent_directory
    use_skymap = config.use_skymap
    email_address_for_job_complete_notice = (
        config.email_address_for_job_complete_notice
    )
    intrinsic_param_to_search = config.intrinsic_param_to_search
    # TODO: handle verbosity levels with `logging` module
#    verbose = True

    is_event = config.event.mode in {"sid", "gid"}

    if not is_event:
        # Start injections workflow
        injections = None
        read_inj_index = 0
        if config.event.injections_file.endswith(".txt"):
            injections = convert_injections_txt_to_objects(
                config.event.injections_file
            )
            read_inj_index = 1
        else:
            xmldoc = ligolw_utils.load_filename(
                config.event.injections_file,
                verbose=True, contenthandler=LIGOLWContentHandler,
            )
            injections = lsctables.SimInspiralTable.get_table(xmldoc)

        inj_index = 0
        n_submitted = 0
        params_all = {}
        n_events = len(injections)
    else:
        n_events = 1

    for event_index in range(n_events):
        os.chdir(init_directory)
        if is_event:
            fmin_template = float(
                config.integrate_likelihood_cmds_dict["fmin-template"]
            )

            # lvalert submission script workflow
            client = GraceDb(config.gracedb_url)
            event = None
            # TODO: check whether we should be getting the submitter name
#            submitter = ""
            packet = ""
            lvalert = False
            if config.event.mode == 'sid':
                sevent = client.superevent(config.event.superevent_id).json()
                gracedb_id = sevent['preferred_event']
            elif config.event.mode == 'gid':
                gracedb_id = config.event.gracedb_id
            else:
                raise RuntimeError(f'Unknown mode {config.event.mode}')
            gracedb_id = get_graceid_after_superevent_check(
                gracedb_id, client,
                output_parent_directory,
                email_address_for_job_complete_notice,
            )

            event = client.event(gracedb_id).json()
            insp_type = event["extra_attributes"]
            pipeline = event["pipeline"]

            print("event info", event)

            # Take the information from the first detector.
            # Template parameters are required to be the same across templates
            # for gstlal.
            coinc = insp_type["CoincInspiral"]

            # Gather event info in format needed for following scripts.
            params = insp_type["SingleInspiral"][0]
            event_info = {}
            # Add a date to this.
            date = str(datetime.date.today()).replace('-', '')  # MOVE TOP
            creation_date = event["created"]
            creation_date = str(creation_date.split(" ")[0].replace("-", ""))
            event_info["output_event_ID"] = (
                f"{date}_{pipeline}_{creation_date}_{gracedb_id}"
            )
            event_info["event_time"] = construct_event_time_string(
                params["end_time"], params["end_time_ns"],
            )
        else:
            inj = injections[event_index]
            event_info = {}
            # TODO: double check this is still used
            if read_inj_index:
                # Note: this is only true for the inj files I generated with
                # generate_injections.
                # Here the index is set to the index in the original injections
                # file.
                inj_index = inj.alpha6
            event_info = config.common_event_info.copy()
            # If the cache file input includes the expression $INJINDEX$ it
            # will be replaced by the inj index
            if config.use_skymap:
                if "$INJINDEX$" in event_info["skymap_file"]:
                    event_info["skymap_file"] = (
                        event_info["skymap_file"].replace(
                            "$INJINDEX$", str(int(inj_index))
                        )
                    )
                if not os.path.isfile(event_info["skymap_file"]):
                    sys.exit(
                        "ERROR: you've requested use_skymap but the skymap"
                        "file you've specified doesn't exist: "
                        + event_info["skymap_file"]
                    )
            if "$INJINDEX$" in event_info["cache_file"]:
                event_info["cache_file"] = (
                    event_info["cache_file"].replace(
                        "$INJINDEX$", str(int(inj_index))
                    )
                )
            if not os.path.isfile(event_info["cache_file"]):
                sys.exit(
                    "ERROR: cache file doesn't exist: "
                    + event_info["cache_file"]
                )
            event_info["output_event_ID"] = f"inj_{inj_index}"
            output_event_directory = event_info["output_event_ID"]
            output_dir = os.path.join(
                init_directory,
                config.output_parent_directory, output_event_directory,
                "",  # NOTE: trailing '/' might not be needed
            )
            event_all_iterations_fname = os.path.join(
                output_dir, "event_all_iterations.dag",
            )
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            elif os.path.isfile(event_all_iterations_fname):
                # Skip this inejction if it has already been submitted
                continue

            event_info["output_event_ID"] = f"inj_{inj_index}"
            event_info[
                "event_time"] = construct_event_time_string(
                inj.geocent_end_time, inj.geocent_end_time_ns,
            )
            params = check_switch_m1m2s1s2({
                "mass1": inj.mass1,
                "mass2": inj.mass2,
                "spin1z": inj.spin1z,
                "spin2z": inj.spin2z,
            })
            params_all[inj_index] = params
            # Save all the true injected values for
            # pp plots or other tests later
            injection_param_list = [
                f"mass1={params['mass1']}",
                f"mass2={params['mass2']}",
                f"spin1z={params['spin1z']}",
                f"spin2z={params['spin2z']}",
                f"longitude={inj.longitude}",
                f"latitude={inj.latitude}",
                f"distance={inj.distance}",
                f"inclination={inj.inclination}",
                f"phase={inj.phi0}",
                f"polarization={inj.psi0}",
            ]
            event_info[
                "injection_param"] = f"[{','.join(injection_param_list)}]"
        if is_event:
            intrinsic_param_list = [
                f"{ip}={params[ip]}"
                for ip in intrinsic_param_to_search
            ]
        else:
            intrinsic_param_list = [
                f"{ip}={params[ip]}"
                for ip in intrinsic_param_to_search
            ]
        event_info[
            "intrinsic_param"] = f"[{','.join(intrinsic_param_list)}]"
        event_info[
            "wrapper_script_start_time"] = time.time()
        # TODO: Clean up this comment, too much detail specific to the time
        # it was written.
        # Determine which approximant should be used based on the total mass
        # the threshold is from the gstlal O2 template bank threshold:
        # https://arxiv.org/pdf/1812.05121.pdf
        # NRHybridSurrogate up to q=8, should work with everything.
        # Review finishing now. Ask Seb?
        # At very high mass, waveform generator will fail. No inspiral phase at
        # very high mass. Waveform generator requires you to start at inspiral
        # phase.
        if is_event:
            if float(params["mass1"])+float(params["mass2"]) > 10.0:
                event_info["approximant"] = "SEOBNRv4_ROM"  # v4 vs v4_ROM
            else:
                if "spin1z" in intrinsic_param_to_search:
                    # SpinTaylorT4 is the fastest for spinning searches.
                    event_info["approximant"] = "SpinTaylorT4"
                else:
                    # TaylorT2 is the fastest in general.
                    event_info["approximant"] = "TaylorT2"

            output_event_directory = event_info["output_event_ID"]
            output_dir = os.path.join(
                init_directory,
                config.output_parent_directory,
                output_event_directory,
                ""  # TODO: confirm trailing '/' is needed
            )
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            if packet != "":
                packet_fname = os.path.join(output_dir, "lvalert_packet.txt")
                with open(packet_fname, "w") as packet_file:
                    print(packet, file=packet_file)

        else:
            if (float(params["mass1"]) +
                    float(params["mass2"])) > 10.0:
                # Note: pp-plots injections used SEOBNRv4, NOT SEOBNRv4_ROM
                event_info["approximant"] = "SEOBNRv4"
            else:
                warnings.warn(
                    "using SEOBNRv4 for BNS********* for testing only"
                )
                # all approximants checked with BNS
                event_info["approximant"] = "TaylorF2"
        os.chdir(output_dir)
        if is_event:
            # The PSD file name is set here, but it's written later because
            # sometimes it takes a while for the file to upload
            psd_filename = os.path.join(output_dir, "psd.xml.gz")
            skymap_filename = os.path.join(output_dir, "bayestar.fits")

            # Now, based on the event_time, find the frame files you want.
            channel_str = "["
            psd_file_str = "["
            for insp in insp_type["SingleInspiral"]:
                channel = insp["channel"]
                ifo = insp["ifo"]
                channel_str += f"{ifo}={channel},"
                psd_file_str += f"{ifo}={psd_filename},"
                logging.info("IFO: %s", ifo)
                # Copied from Richards code
                # https://git.ligo.org/richard-oshaughnessy/research-projects-RIT/blob/temp-RIT-Tides-port_master-GPUIntegration/MonteCarloMarginalizeCode/Code/helper_LDG_Events.py
                # Estimate signal duration
                t_event = insp["end_time"]
                P = lalsimutils.ChooseWaveformParams()
                P.m1 = insp["mass1"]*lal.MSUN_SI
                P.m2 = insp["mass2"]*lal.MSUN_SI
                P.fmin = fmin_template
                P.tref = t_event
                logging.debug("P: %s, %s, %s", P.m1, P.m2, P.fmin)
                t_duration = max(
                    coinc["minimum_duration"],
                    lalsimutils.estimateWaveformDuration(P),
                )
                logging.info(
                    "DONE Estimate duration: %s, %s, %s",
                    t_duration,
                    coinc["minimum_duration"],
                    lalsimutils.estimateWaveformDuration(P)
                )
                # Buffer for inverse spectrum truncation.
                t_before = max(4, t_duration) * 1.2 + 30
                # TODO: double-check these parentheses are intentionally placed
                data_start_time = int(t_event - int(t_before))
                data_end_time = int(t_event + 500)

                data_type = (
                    f"{ifo}Online" if ifo == "V1" else f"{ifo}_HOFT_C00"
                )
                # TODO: We should import gwdatafind and call the underlying
                #       functions directly.
                dcmd = (
                    "python -m gwdatafind -u file "
                    f"-o {ifo[0]} -t {data_type} -s {data_start_time} "
                    f"-e {data_end_time} > {ifo[0]}_raw.cache"
                )
                logging.info(dcmd)
                exit_status = os.system(dcmd)
                if exit_status != 0:
                    logging.error(dcmd)
                    sys.exit(f"ERROR: non zero exit status {exit_status}")

            # path2cache always assumes data is in output_dir, so that path
            # needs to be removed before passing output to data.cache
            text_for_sed_removal = "localhost{}file:\\/".format(
                output_dir.replace('/', '\\/')
            )
            os.system(
                "cat *_raw.cache "
                "| lalapps_path2cache "
                f"| sed 's/{text_for_sed_removal}//g' > data.cache"
            )

            # Check if the data.cache file is empty
            if os.stat("data.cache").st_size == 0:
                if lvalert and email_address_for_job_complete_notice != "":
                    email_cmd = (
                        f"Failed Lvalert, no data at trigger time "
                        f"{gracedb_id} | mail -s {output_parent_directory} "
                        f"          {email_address_for_job_complete_notice}"
                    )
                    # TODO: Instead of system call, should use Python's
                    # standard email modules
                    os.system(email_cmd)

                sys.exit(
                    "ERROR: There is no data at the time when this triggered, "
                    "how can that happen?"
                )
            # Put together cache file
            event_info["cache_file"] = os.path.join(output_dir, "data.cache")
            event_info["psd_file"] = psd_file_str[:-1] + "]"
            event_info["channel_name"] = channel_str[:-1] + "]"

        if config.submit_only_at_exact_signal_position:
            # Only submit one integrate job at the exact signal position
            script_path = "create_submit_at_exact_signal_position.py"
            cmd = f"{script_path} {cfgname} '{json.dumps(event_info)}'"
            run_cmd(cmd)
        else:
            # Create the initial grid for this event
            intrinsic_param = convert_list_string_to_dict(
                event_info["intrinsic_param"]
            )
            exe = config.exe_grid_refine
            if config.initial_grid_setup.mode != "overlap_bank":
                sys.exit("ERROR: We currenly only support overlap bank runs")

            intrinsic_grid_name_base = "intrinsic_grid"
            initial_grid_xml = intrinsic_grid_name_base+"_iteration_0.xml.gz"
            initial_grid_hdf = intrinsic_grid_name_base+"_all_iterations.hdf"
            # now fill in the rest
            cmd = (
                f"{exe} --verbose --no-exact-match --setup "
                f"{initial_grid_hdf} --output-xml-file-name {initial_grid_xml}"
            )
            if config.distance_coordinates != "":
                cmd += " -d "+config.distance_coordinates

            # Add the event trigger parameters, the inital grid will include
            # all points in the overlap bank with overlap < the -T value
            for param, val in intrinsic_param.items():
                print(param, val)
                cmd += " -i "+param+"="+str(val)
            cmd += config.initial_grid_only_cli_args

            # Apply the parameter limits from
            # the 'initial_region' config option.
            if config.initial_grid_setup.initial_region is not None:
                for (
                    param,
                    vals,
                ) in config.initial_grid_setup.initial_region.items():
                    if len(vals) != 2:
                        raise ValueError(
                            f"Expected 2 values for parameter {param} in "
                            f"'initial_region', got {len(vals)} instead."
                        )

                    val_lo, val_hi = vals
                    cmd += f" -I {param}={val_lo},{val_hi}"
            else:
                # The overlap files are split by Mchirp, it takes time to check all
                # files and see which one contains our signal. Here, we check the
                m1 = float(intrinsic_param["mass1"])
                m2 = float(intrinsic_param["mass2"])
                s1 = s2 = 0
                if "spin1z" in intrinsic_param:
                    s1 = float(intrinsic_param["spin1z"])
                    s2 = float(intrinsic_param["spin2z"])

                chi_eff_event = transform_s1zs2z_chi(m1, m2, s1, s2)
                Mchirp_event = ((m1*m2)**(3/5.0))/((m1 + m2)**(1/5.0))
                eta_event = ((m1*m2)/((m1+m2)**2.))
                print("Event mchirp", Mchirp_event, eta_event)

                # Reducing list of files to those in mchirp range
                olap_filenames = glob.glob(config.initial_grid_setup.overlap_bank)
                count_files = 0
                # strings_to_include = "{"
                min_dist = -1
                min_dist_filename = ""

                # TODO: Note that if we provide one file, it's always used, but if
                #       we provide multiple, there's a possibility no file contains
                #       the template, and we error out.  So providing `A.hdf` might
                #       work, but providing `A.hdf` and `B.hdf` triggers an error.
                #       This seems like bad behavior and should be addressed.
                if len(olap_filenames) == 0:
                    sys.exit("ERROR: no overlap files found")
                elif len(olap_filenames) == 1:
                    count_files = 1
                    cmd += f" --use-overlap {olap_filenames[0]}"
                else:
                    for hdf_filename in olap_filenames:
                        with h5py.File(hdf_filename, "r") as h5file:
                            wfrm_fam = next(iter(h5file.keys()))
                            mdata = h5file[wfrm_fam]
                            m1, m2 = mdata["mass1"][:], mdata["mass2"][:]
                            ntemplates = len(mdata["overlaps"])
                            m1, m2 = (
                                mdata["mass1"][:ntemplates],
                                mdata["mass2"][:ntemplates]
                            )
                            Mchirps = ((m1*m2)**(3/5.0))/((m1+m2)**(1/5.0))
                            if min(Mchirps) <= Mchirp_event <= max(Mchirps):
                                print(hdf_filename)
                                s1, s2 = (
                                    mdata["spin1z"][:ntemplates],
                                    mdata["spin2z"][:ntemplates]
                                )
                                etas = ((m1*m2)/((m1+m2)**2.))
                                chi_effs = transform_s1zs2z_chi(m1, m2, s1, s2)
                                # FIXME: even if youre not searching over spin, you
                                #        want to find the file with the closest
                                #        template assuming spin=0 implement above
                                #        here at same time as code
                                list_for_tree = np.asarray([Mchirps, etas]).T
                                pt = np.asarray([Mchirp_event, eta_event])
                                if "spin1z" in intrinsic_param:
                                    list_for_tree = np.asarray(
                                        [Mchirps, etas, chi_effs]
                                    ).T
                                    pt = np.asarray([
                                        Mchirp_event,
                                        eta_event,
                                        chi_eff_event
                                    ])

                                tree = BallTree(list_for_tree)
                                dist, m_idx = tree.query(np.atleast_2d(pt), k=1)
                                if dist < min_dist or min_dist_filename == "":
                                    min_dist = dist
                                    min_dist_filename = hdf_filename

                                count_files += 1
                                cmd += f" --use-overlap {hdf_filename}"
                    if count_files == 0:
                        sys.exit("ERROR: No overlap files found")

            logging.info(cmd)
            exit_status = os.system(cmd)
            if exit_status != 0:
                logging.error(cmd)
                sys.exit("ERROR: non zero exit status"+str(exit_status))

            print(
                f"[initial_grid_xml={initial_grid_xml},"
                f"initial_grid_hdf={initial_grid_hdf}]"
            )

        intrinsic_grid_name_base = "intrinsic_grid"
        event_info["initial_grid_xml"] = (
            f"{intrinsic_grid_name_base}_iteration_0.xml.gz"
        )
        event_info["initial_grid_hdf"] = (
            f"{intrinsic_grid_name_base}_all_iterations.hdf"
        )

        if is_event:
            # Get the psd file and write locally
            # This is done after the intrinsic grid generation because
            # sometimes the file takes time to upload.

            with open(psd_filename, 'wb') as psdfileobj:
                try:
                    logging.info(
                        f"Downloading psd.xml.gz from {gracedb_id} ...")
                    r = client.files(gracedb_id, 'psd.xml.gz')
                    logging.info(
                        "psd.xml.gz has been successfully downloaded.")
                except HTTPError:
                    logging.info(
                        "psd.xml.gz was not successfully downloaded. "
                        "Trying coinc.xml instead ...")
                    r = client.files(gracedb_id, 'coinc.xml')
                    logging.info("coinc.xml has been successfully downloaded.")
                logging.info(r.headers)
                for line in r:
                    psdfileobj.write(line)

            if use_skymap:
                with open(skymap_filename, 'wb') as skymapfileobj:
                    if config.event.superevent_id:
                        r = client.files(
                            config.event.superevent_id, 'bayestar.fits.gz'
                        )
                    else:
                        r = client.files(
                            gracedb_id, 'bayestar.multiorder.fits'
                        )
                    for line in r:
                        skymapfileobj.write(line)

                event_info["skymap_file"] = skymap_filename
        # Run create_submit_dag
        script_path = "create_submit_dag_one_event.py"
        cmd = f"{script_path} {cfgname} '{json.dumps(event_info)}'"
        logging.info(cmd)
        exit_status = os.system(cmd)
        if exit_status != 0:
            logging.error(cmd)
            sys.exit(f"ERROR: non zero exit status {exit_status}")
        elif email_address_for_job_complete_notice != "":
            email_cmd = (
                f"echo 'Sent for dag submission {json.dumps(event_info)}' "
                f"| mail -s 'rapidPE:{output_parent_directory}' "
                f"          {email_address_for_job_complete_notice}"
            )
            os.system(email_cmd)
        if not is_event:
            logging.info("Events submitted %s", inj_index)
            n_submitted += 1
            if n_submitted % 10 != 0:
                logging.warning("Waiting for 30 seconds!!!!")
                time.sleep(30)
            if not read_inj_index:
                inj_index += 1


def get_graceid_after_superevent_check(
        gid, client,
        output_parent_directory, email_address_for_job_complete_notice,
        packet=None,
):
    '''
    If the event is a superevent get the graceDB ID from the preferred event

    If the preferred event is a CWB event
    (i.e. it doesn't have m1 m2 end_time), get a gstlal ID
    (highest snr gstlal).

    If there's no gstlal ID, choose another CBC ID by highest snr.

    If it's only a CWB event, ignore.
    '''
    other_gids = None
    if "S" in gid:
        if packet is None:
            sevent = client.superevent(gid).json()
            # Set the args.graceid to the preferred event id
            gid = sevent["preferred_event"]
            other_gids = sevent["gw_events"]
        else:
            # Set the args.graceid to the preferred event id
            gid = packet["object"]["preferred_event"]
            other_gids = packet["object"]["gw_events"]

    event = client.event(gid).json()
    pipeline = event["pipeline"]
    # CWB is unmodelled, it doesn't have a m1m2s1s2 to start with.
    # We want to use a modelled gracedb event
    if pipeline not in _allowed_pipelines:
        if other_gids is None:
            sys.exit(
                "ERROR: can't submit rapidPE for non-cbc events. "
                "They're unmodelled, i.e. no intrinsic point to start with. "
                f"{pipeline =}"
            )
        elif len(other_gids) == 1:
            gid = -1
        else:
            # Get the pipelines and snrs for each graceDB ID, choose one.
            cbcgid = prev_snr = -1
            for tmpid in other_gids:
                if not tmpid == gid:
                    event = client.event(tmpid).json()
                    if not event["pipeline"] in _allowed_pipelines:
                        continue
                    else:
                        snr = event["snr"]
                        if snr > prev_snr:
                            cbcgid = tmpid
                            prev_snr = snr
            gid = cbcgid

    if gid == -1:
        # If this is an lvalert, want to send an email explaining there was an
        # interesting event but it wasn't pursued.
        if packet is not None:
            email_cmd = (
                "echo 'Unmodelled Lvalert, no cbc entries available, ignoring."
                      f" {gid} "  # noqa: E131
                f"| mail -s 'rapidPE:{output_parent_directory}'"
                f"          {email_address_for_job_complete_notice}"
            )
            os.system(email_cmd)

        sys.exit(
            "ERROR: Only non-cbc event(s) for this (super)event. "
            f"Can't submit rapidpe. gids={other_gids}"
        )
    else:
        return gid


if __name__ == '__main__':
    main()
