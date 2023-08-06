__author__ = "Vinaya Valsan"
import sys

import ast
import re
import matplotlib
import glob
import numpy as np
import matplotlib.pyplot as plt
import logging
import h5py

from rapid_pe import amrlib
from ligo.lw import utils, lsctables, ligolw

lsctables.use_in(ligolw.LIGOLWContentHandler)
matplotlib.use("Agg")
print("-------------------Plotting intrinsic posteriors----------------------")

logging.basicConfig(level=logging.INFO)


inj_dir = sys.argv[1]
# remove the color codes, because for whatever reason they're included on uwm.
inj_dir = inj_dir.replace("\x1b[0m", "")
inj_dir = inj_dir.replace("\x1b[01;34m", "")
inj_dir = inj_dir.replace("\x1b[K", "")

results_dir = inj_dir + "/results/"
intrinsic_param_str = sys.argv[2]

intrinsic_param = intrinsic_param_str.split("_")

if len(sys.argv) > 3:
    output_dir = sys.argv[3]
else:
    output_dir = inj_dir

f_lower = 40

# Get injection/search point
event_info = open(inj_dir + "/event_info_dict.txt", "r")
contents = event_info.read()
dictionary = ast.literal_eval(contents)
intrinsic_param_inj = dictionary["intrinsic_param"]
mass1_inj = re.search('mass1=(.+?)"', intrinsic_param_inj)
mass1_inj = mass1_inj.group(1)
mass1_inj = float(mass1_inj)
mass2_inj = re.search('mass2=(.+?)"', intrinsic_param_inj)
mass2_inj = mass2_inj.group(1)
mass2_inj = float(mass2_inj)

inj_param_dict = {"mass1": mass1_inj, "mass2": mass2_inj}

spin1z_inj = None
spin2z_inj = None
try:
    spin1z_inj = re.search('spin1z=(.+?)"', intrinsic_param_inj)
    spin1z_inj = spin1z_inj.group(1)
    spin1z_inj = float(spin1z_inj)
    spin2z_inj = re.search('spin2z=(.+?)"', intrinsic_param_inj)
    spin2z_inj = spin2z_inj.group(1)
    spin2z_inj = float(spin2z_inj)
    inj_param_dict["spin1z"] = spin1z_inj
    inj_param_dict["spin2z"] = spin2z_inj
    (
        inj_param_dict["chi_eff"],
        inj_param_dict["chi_a"],
    ) = amrlib.transform_s1zs2z_chi_eff_chi_a(
        mass1_inj, mass2_inj, spin1z_inj, spin2z_inj
    )
except:
    logging.info("No Spin information found in event_info_dict.txt")
    pass

mchirp_inj, eta_inj = amrlib.transform_m1m2_mceta(mass1_inj, mass2_inj)
inj_param_dict["mchirp"] = mchirp_inj
inj_param_dict["eta"] = eta_inj
if "mu1" in intrinsic_param:
    (
        mu1_inj,
        mu2_inj,
        q_inj,
        spin2z_inj,
    ) = amrlib.transform_m1m2s1zs2z_mu1mu2qs2z(
        mass1_inj, mass2_inj, spin1z_inj, spin2z_inj
    )
    inj_param_dict["mu1"] = mu1_inj
    inj_param_dict["mu2"] = mu2_inj
    inj_param_dict["q"] = q_inj
    inj_param_dict["spin2z"] = spin2z_inj
elif "tau0" in intrinsic_param:
    tau0_inj, tau3_inj = amrlib.transform_m1m2_tau0tau3(mass1_inj, mass2_inj)
    inj_param_dict["tau0"] = tau0_inj
    inj_param_dict["tau3"] = tau3_inj
elif "q" in intrinsic_param:
    inj_param_dict["q"] = mass2_inj / mass1_inj


# Read results xml files

all_xml = glob.glob(results_dir + "ILE_iteration_*-MASS_SET_*-0.xml.gz")
if len(all_xml) == 0:
    all_xml = glob.glob(results_dir + "ILE_iteration_*-MASS_SET_*_0_.xml.gz")
print(glob.glob(results_dir + "ILE_iteration_*-MASS_SET_*_0_.xml.gz"))
print(f"Found {len(all_xml)} sample files")
iterations = [
    xmlfile[
        xmlfile.find("ILE_iteration"): xmlfile.find("ILE_iteration")
        + len("ILE_iteration_0")
    ]
    for xmlfile in all_xml
]

grid_levels = np.sort(np.unique(iterations))
Mass1 = []
Mass2 = []
Spin1z = []
Spin2z = []
Margll = []
grid_id = []
for i, gl in enumerate(grid_levels):
    xml_files = glob.glob(results_dir + gl + "-MASS_SET_*-0.xml.gz")
    if len(xml_files) == 0:
        xml_files = glob.glob(results_dir + gl + "-MASS_SET_*_0_.xml.gz")
    print(f"Found {len(xml_files)} in grid_level {gl}")
    for xml_file in xml_files:
        xmldoc = utils.load_filename(
            xml_file, contenthandler=ligolw.LIGOLWContentHandler
        )
        new_tbl = lsctables.SnglInspiralTable.get_table(xmldoc)
        for row in new_tbl:
            Mass1.append(row.mass1)
            Mass2.append(row.mass2)
            Margll.append(row.snr)
            grid_id.append(i)
            if spin1z_inj is not None:
                Spin1z.append(row.spin1z)
                Spin2z.append(row.spin2z)
Mass1 = np.asarray(Mass1)
Mass2 = np.asarray(Mass2)
Margll = np.asarray(Margll)
intrinsic_param_dict = {"mass1": Mass1, "mass2": Mass2}
if spin1z_inj is not None:
    Spin1z = np.asarray(Spin1z)
    Spin2z = np.asarray(Spin2z)
    intrinsic_param_dict["spin1z"] = Spin1z
    intrinsic_param_dict["spin2z"] = Spin2z
    (
        intrinsic_param_dict["chi_eff"],
        intrinsic_param_dict["chi_a"],
    ) = amrlib.transform_s1zs2z_chi_eff_chi_a(Mass1, Mass2, Spin1z, Spin2z)
Mchirp, Eta = amrlib.transform_m1m2_mceta(Mass1, Mass2)
intrinsic_param_dict["mchirp"] = Mchirp
intrinsic_param_dict["eta"] = Eta
if "mu1" in intrinsic_param:
    Mu1, Mu2, Q, Spin2z = amrlib.transform_m1m2s1zs2z_mu1mu2qs2z(
        Mass1, Mass2, Spin1z, Spin2z
    )
    intrinsic_param_dict["mu1"] = Mu1
    intrinsic_param_dict["mu2"] = Mu2
    intrinsic_param_dict["q"] = Q
    intrinsic_param_dict["spin2z"] = Spin2z
elif "tau0" in intrinsic_param:
    Tau0, Tau3 = amrlib.transform_m1m2_tau0tau3(Mass1, Mass2)
    intrinsic_param_dict["tau0"] = Tau0
    intrinsic_param_dict["tau3"] = Tau3
elif "q" in intrinsic_param:
    intrinsic_param_dict["q"] = Mass2 / Mass1
for key in intrinsic_param_dict.keys():
    print(
        f"{key}: min = {np.min(intrinsic_param_dict[key])},"
        f"max =  {np.max(intrinsic_param_dict[key])}"
    )


margL = np.exp(Margll)
# margL = margL / (np.amax(margL))

grid_0_inds = np.where(np.array(grid_id) == 0)[0]


def plot_grid(param1, param2, grid_level=None):
    """
    plot grid alignment for param1 and param2 and a specific grid level.

    Valid grid_level = 0,1,2,3,....None

    Valid param1 and param2 = mass1, mass2, mchirp, eta, spin1z, spin2z,
                              mu1, mu2, q, tau0, tau3

    grid_level=None plots the grid point from all grid levels

    """
    logging.info(
        f"plotting grids for {param1} and {param2} on grid_level={grid_level}"
    )
    all_weights = np.log(margL)
    if grid_level is not None:
        grid_inds = np.where(np.array(grid_id) == grid_level)[0]
        data1 = intrinsic_param_dict[param1][grid_inds]
        data2 = intrinsic_param_dict[param2][grid_inds]
        weight = np.log(margL[grid_inds])
        print(f"min({param1}) = {np.min(data1)}, max({param1}) = {np.max(data1)}")
        print(f"min({param2}) = {np.min(data2)}, max({param2}) = {np.max(data2)}")
    else:
        data1 = intrinsic_param_dict[param1]
        data2 = intrinsic_param_dict[param2]
        weight = np.log(margL)
        print(f"min({param1}) = {np.min(data1)}, max({param1}) = {np.max(data1)}")
        print(f"min({param2}) = {np.min(data2)}, max({param2}) = {np.max(data2)}")
    plt.figure()
    plt.scatter(data1, data2, c=weight,vmin=np.min(all_weights),vmax=np.max(all_weights))
    plt.plot(inj_param_dict[param1], inj_param_dict[param2], "r*")
    plt.xlabel(param1)
    plt.ylabel(param2)
    plt.xlim(
        np.min(intrinsic_param_dict[param1]), np.max(intrinsic_param_dict[param1])
    )
    plt.ylim(
        np.min(intrinsic_param_dict[param2]), np.max(intrinsic_param_dict[param2])
    )
    if grid_level is not None:
        plt.title("grid_level = " + str(grid_level))
    else:
        plt.title("all grids")
    plt.colorbar(label=r"$log(L_{marg})$")
    if grid_level is not None:
        filename = (
            f"{output_dir}/summary_plots/grid_{param1}"
            f"_{param2}_iteration-{str(grid_level)}.png"
        )
    else:
        filename = f"{output_dir}/summary_plots/grid_{param1}_{param2}_all.png"
    plt.savefig(filename)
    return


print("grid_level", grid_levels)
for i, gl in enumerate(grid_levels):
    plot_grid("mass1", "mass2", grid_level=i)
    plot_grid("mchirp", "eta", grid_level=i)

    if spin1z_inj is not None:
        plot_grid("spin1z", "spin2z", grid_level=i)

    if "mu1" in intrinsic_param:
        plot_grid("mu1", "mu2", grid_level=i)
        plot_grid("q", "spin1z", grid_level=i)
        plot_grid("q", "spin2z", grid_level=i)

    if "tau0" in intrinsic_param:
        plot_grid("tau0", "tau3", grid_level=i)

plot_grid("mass1", "mass2")
plot_grid("mchirp", "eta")
if spin1z_inj is not None:
    plot_grid("spin1z", "spin2z")
if "mu1" in intrinsic_param:
    plot_grid("mu1", "mu2")
    plot_grid("q", "spin1z")
    plot_grid("q", "spin2z")
elif "tau0" in intrinsic_param:
    plot_grid("tau0", "tau3")
elif "q" in intrinsic_param:
    plot_grid("mchirp", "q")


def find_sigma(param, grid_level=None):
    param_list = np.array(intrinsic_param_dict[param])

    if grid_level is not None:
        grid_inds = np.where(np.array(grid_id) == grid_level)[0]
        param_list = np.array(intrinsic_param_dict[param])[grid_inds]
    Sigma = []
    for j in range(len(param_list)):
        distance_array = np.array(
            [
                abs(param_list[j] - param_list[i])
                for i in range(len(param_list))
            ]
        )
        distance_array = np.sort(distance_array[distance_array > 1e-5])
        sigma = distance_array[0]
        Sigma.append(sigma)
    return Sigma


mass_params_for_posterior = intrinsic_param[0:2]


def uniform_m1_m2_prior_in_mchirp_eta(mchirp, eta):
    """
    Returns  jacobian  p(mchirp, eta) = d(mass1,mass2)/d(mchirp,eta)
    """
    p = np.abs(
        mchirp * np.power(eta, -6.0 / 5.0) * (1.0 / np.sqrt(1.0 - 4.0 * eta))
    )
    return p


def uniform_m1_m2_prior_in_mchirp_q(mchirp, q):
    """
    Returns  jacobian  p(mchirp, q) = d(mass1,mass2)/d(mchirp,q)
    """
    p = np.abs(mchirp * (1.0 + q) ** 2 / 5 / q ** (6 / 5))
    return p


# def uniform_m1_m2_prior_in_tau0_tau3(tau0, tau3, f_lower):
#    """
#    Returns  jacobian  p(tau0, tau3) = d(mass1,mass2)/d(tau0,tau3)
#    """
#    m1, m2 = amrlib.transform_tau0tau3_m1m2(tau0, tau3, f_lower)
#    num = (
#        165888.0
#        * f_lower ** (13.0 / 3.0)
#        * m1 ** 3.0
#        * (m1 - m2)
#        * m2 ** 3.0
#        * (m1 + m2)
#        * (4.0 / 3.0)
#        * np.pi ** (10.0 / 3.0)
#    )
#    den = (
#        5.0
#        * (m1 - 3 * m2)
#        * (3.0 * m1 - m2)
#        * (3.0 * m1 + 2.0 * m2)
#        * (2.0 * m1 + 3.0 * m2)
#    )
#    p = np.abs((num / den))
#    return p
#


def uniform_m1_m2_prior_in_tau0_tau3(tau0, tau3, f_lower):
    """
    Returns  jacobian  p(tau0, tau3) = d(mass1,mass2)/d(tau0,tau3)
    """
    a3 = np.pi / (8.0 * (np.pi * f_lower) ** (5.0 / 3.0))
    a0 = 5.0 / (256.0 * (np.pi * f_lower) ** (8.0 / 3.0))
    tmp1 = (a0 * tau3) / (a3 * tau0)
    num = a0 * (tmp1) ** (1.0 / 3.0)
    tmp2 = 1 - ((4 * a3) / (tau3 * tmp1 ** (2.0 / 3.0)))
    den = tau0 ** 2.0 * tau3 * np.sqrt(tmp2)
    return np.abs(num / den)


def uniform_m1m2chi1chi2_prior_to_mu1mu2qchi2(mu1, mu2, q, s2z):
    """Return d(mu1, mu2, q, s2z) / d(m1, m2, s1z, s2z)"""
    MsunToTime = 4.92659 * 10.0 ** (
        -6.0
    )  # conversion from solar mass to seconds
    fref_mu = 200.0
    # coefficients of mu1 and mu2
    mu_coeffs = np.array(
        [
            [0.97437198, 0.20868103, 0.08397302],
            [-0.22132704, 0.82273827, 0.52356096],
        ]
    )
    m1, m2, s1z, s2z = amrlib.transform_mu1mu2qs2z_m1m2s1zs2z(mu1, mu2, q, s2z)
    mc = (m1 * m2) ** (3.0 / 5.0) / (m1 + m2) ** (1.0 / 5.0)
    q = m2 / m1
    eta = amrlib.qToeta(q)
    x = np.pi * mc * MsunToTime * fref_mu
    tmp1 = (
        mu_coeffs[0, 2] * mu_coeffs[1, 0] - mu_coeffs[0, 0] * mu_coeffs[1, 2]
    )
    tmp2 = (
        mu_coeffs[0, 2] * mu_coeffs[1, 1] - mu_coeffs[0, 1] * mu_coeffs[1, 2]
    )
    denominator = (
        x
        * 5.0
        * (113.0 + 75.0 * q)
        * (
            252.0 * tmp1 * q * eta ** (-3.0 / 5.0)
            + tmp2 * (743.0 + 2410.0 * q + 743.0 * q ** 2.0) * x ** (2.0 / 3.0)
        )
    )
    numerator = (
        m1 ** 2.0 * 4128768.0 * q * (1.0 + q) ** 2.0 * x ** (10.0 / 3.0)
    )
    return np.abs(numerator / denominator)


def get_posterior_samples_for_m1m2(intrinsic_param_str, grid_level=None):
    """
    Generate posterior samples for params for the given grid_level
    """
    params = intrinsic_param_str.split("_")
    sample_dict = {}
    param1_name = params[0]
    param2_name = params[1]
    if spin1z_inj is not None:
        if intrinsic_param_str == "mu1_mu2_q_s2q":
            param3_name = "q"
            param4_name = "spin2z"
        else:
            param3_name = "chi_eff"
            param4_name = "chi_a"
    if grid_level is not None:
        grid_inds = np.where(np.array(grid_id) == grid_level)[0]
        param1 = intrinsic_param_dict[param1_name][grid_inds]
        param2 = intrinsic_param_dict[param2_name][grid_inds]
        if spin1z_inj is not None:
            param3 = intrinsic_param_dict[param3_name][grid_inds]
            param4 = intrinsic_param_dict[param4_name][grid_inds]
        margL_sel = margL[grid_inds]
        margL_normed = (margL_sel - np.min(margL)) / (np.max(margL) - np.min(margL))
    else:
        param1 = intrinsic_param_dict[param1_name]
        param2 = intrinsic_param_dict[param2_name]
        if spin1z_inj is not None:
            param3 = intrinsic_param_dict[param3_name]
            param4 = intrinsic_param_dict[param4_name]
        margL_normed = (margL - np.min(margL)) / (np.max(margL) - np.min(margL))
    sigma1 = find_sigma(param1_name, grid_level)
    sigma2 = find_sigma(param2_name, grid_level)
    if spin1z_inj is not None:
        sigma3 = find_sigma(param3_name, grid_level)
        sigma4 = find_sigma(param4_name, grid_level)
    N = 50000 * margL_normed / (sum(margL_normed))
    param1_samples = []
    param2_samples = []
    param3_samples = []
    param4_samples = []
    for i in range(len(param1)):
        random_param1 = np.random.normal(
            loc=param1[i], scale=sigma1[i], size=int(N[i])
        )
        random_param2 = np.random.normal(
            loc=param2[i], scale=sigma2[i], size=int(N[i])
        )
        param1_samples = np.append(param1_samples, random_param1)
        param2_samples = np.append(param2_samples, random_param2)
        if spin1z_inj is not None:

            random_param3 = np.random.normal(
                loc=param3[i], scale=sigma3[i], size=int(N[i])
            )
            random_param4 = np.random.normal(
                loc=param4[i], scale=sigma4[i], size=int(N[i])
            )
            param3_samples = np.append(param3_samples, random_param3)
            param4_samples = np.append(param4_samples, random_param4)

    if intrinsic_param_str == "mchirp_eta":
        mask = amrlib.check_mchirpeta(param1_samples, param2_samples)
        if spin1z_inj is not None:
            mask &= amrlib.check_spins(param3_samples)
            mask &= amrlib.check_spins(param4_samples)
            chi_eff_samples = np.array(param3_samples[mask])
            chi_a_samples = np.array(param4_samples[mask])

        mc_samples = np.array(param1_samples[mask])
        eta_samples = np.array(param2_samples[mask])
        m1_samples, m2_samples = amrlib.transform_mceta_m1m2(
            mc_samples, eta_samples
        )
        mceta_prior = uniform_m1_m2_prior_in_mchirp_eta(
            mc_samples, eta_samples
        )
        sample_dict["mass1"] = m1_samples
        sample_dict["mass2"] = m2_samples
        sample_dict["mchirp"] = mc_samples
        sample_dict["eta"] = eta_samples
        sample_dict["mceta_prior"] = mceta_prior
        if spin1z_inj is not None:
            (
                spin1z_samples,
                spin2z_samples,
            ) = amrlib.transform_chi_eff_chi_a_s1zs2z(
                m1_samples, m2_samples, chi_eff_samples, chi_a_samples
            )

            sample_dict["chi_eff"] = chi_eff_samples
            sample_dict["chi_a"] = chi_a_samples
            sample_dict["spin1z"] = spin1z_samples
            sample_dict["spin2z"] = spin2z_samples
    elif intrinsic_param_str == "mass1_mass2":
        mask = amrlib.check_mass1mass2(param1_samples, param2_samples)
        if spin1z_inj is not None:
            mask &= amrlib.check_spins(param3_samples)
            mask &= amrlib.check_spins(param4_samples)
            chi_eff_samples = np.array(param3_samples[mask])
            chi_a_samples = np.array(param4_samples[mask])
        m1_samples = param1_samples[mask]
        m2_samples = param2_samples[mask]
        mc_samples, eta_samples = amrlib.transform_m1m2_mceta(
            m1_samples, m2_samples
        )
        mceta_prior = uniform_m1_m2_prior_in_mchirp_eta(
            mc_samples, eta_samples
        )
        sample_dict["mass1"] = m1_samples
        sample_dict["mass2"] = m2_samples
        sample_dict["mchirp"] = mc_samples
        sample_dict["eta"] = eta_samples
        sample_dict["mceta_prior"] = mceta_prior
        if spin1z_inj is not None:
            (
                spin1z_samples,
                spin2z_samples,
            ) = amrlib.transform_chi_eff_chi_a_s1zs2z(
                m1_samples, m2_samples, chi_eff_samples, chi_a_samples
            )
            sample_dict["chi_eff"] = chi_eff_samples
            sample_dict["chi_a"] = chi_a_samples
            sample_dict["spin1z"] = spin1z_samples
            sample_dict["spin2z"] = spin2z_samples
    elif intrinsic_param_str == "tau0_tau3":
        mask = amrlib.check_tau0tau3(param1_samples, param2_samples)
        if spin1z_inj is not None:
            mask &= amrlib.check_spins(param3_samples)
            mask &= amrlib.check_spins(param4_samples)
            chi_eff_samples = np.array(param3_samples[mask])
            chi_a_samples = np.array(param4_samples[mask])

        tau0_samples = np.array(param1_samples[mask])
        tau3_samples = np.array(param2_samples[mask])
        m1_samples, m2_samples = amrlib.transform_tau0tau3_m1m2(
            tau0_samples, tau3_samples
        )
        mc_samples, eta_samples = amrlib.transform_m1m2_mceta(
            m1_samples, m2_samples
        )
        tau0tau3_prior = uniform_m1_m2_prior_in_tau0_tau3(
            tau0_samples, tau3_samples, f_lower
        )
        mceta_prior = uniform_m1_m2_prior_in_mchirp_eta(
            mc_samples, eta_samples
        )
        sample_dict["mass1"] = m1_samples
        sample_dict["mass2"] = m2_samples
        sample_dict["tau0"] = tau0_samples
        sample_dict["tau3"] = tau3_samples
        sample_dict["mchirp"] = mc_samples
        sample_dict["eta"] = eta_samples
        sample_dict["mceta_prior"] = mceta_prior
        sample_dict["tau0tau3_prior"] = tau0tau3_prior
        if spin1z_inj is not None:
            (
                spin1z_samples,
                spin2z_samples,
            ) = amrlib.transform_chi_eff_chi_a_s1zs2z(
                m1_samples, m2_samples, chi_eff_samples, chi_a_samples
            )
            sample_dict["chi_eff"] = chi_eff_samples
            sample_dict["chi_a"] = chi_a_samples
            sample_dict["spin1z"] = spin1z_samples
            sample_dict["spin2z"] = spin2z_samples
    elif intrinsic_param_str == "mchirp_q":
        mask = (
            amrlib.check_q(param2_samples)
            & (param1_samples > 0)
            & (param2_samples <= 1)
        )
        if spin1z_inj is not None:
            mask &= amrlib.check_spins(param3_samples)
            mask &= amrlib.check_spins(param4_samples)
            chi_eff_samples = np.array(param3_samples[mask])
            chi_a_samples = np.array(param4_samples[mask])
        mc_samples = np.array(param1_samples[mask])
        q_samples = np.array(param2_samples[mask])

        sample_dict["mchirp"] = mc_samples
        sample_dict["q"] = q_samples
        sample_dict["mass1"], sample_dict["mass2"] = amrlib.transform_mcq_m1m2(
            mc_samples, q_samples
        )
        sample_dict["eta"] = amrlib.qToeta(q_samples)
        sample_dict["mcq_prior"] = uniform_m1_m2_prior_in_mchirp_q(
            mc_samples, q_samples
        )
        if spin1z_inj is not None:
            (
                spin1z_samples,
                spin2z_samples,
            ) = amrlib.transform_chi_eff_chi_a_s1zs2z(
                m1_samples, m2_samples, chi_eff_samples, chi_a_samples
            )
            sample_dict["chi_eff"] = chi_eff_samples
            sample_dict["chi_a"] = chi_a_samples
            sample_dict["spin1z"] = spin1z_samples
            sample_dict["spin2z"] = spin2z_samples
    elif param1_name == "mu1" and param2_name == "mu2":
        mask = amrlib.check_q(param3_samples)
        mask &= amrlib.check_spins(param4_samples)
        mu1_samples = np.array(param3_samples[mask])
        mu2_samples = np.array(param4_samples[mask])
        q_samples = np.array(param1_samples[mask])
        spin2z_samples = np.array(param2_samples[mask])

        (
            m1_samples,
            m2_samples,
            spin1z_samples,
            spin2z_samples,
        ) = amrlib.transform_mu1mu2qs2z_m1m2s1zs2z(
            mu1_samples, mu2_samples, q_samples, spin2z_samples
        )
        mass_spin_mask = amrlib.check_mass1mass2(m1_samples, m2_samples)
        mass_spin_mask &= amrlib.check_spins(spin1z_samples)
        mass_spin_mask &= amrlib.check_spins(spin2z_samples)

        m1_samples = m1_samples[mass_spin_mask]
        m2_samples = m2_samples[mass_spin_mask]
        spin1z_samples = spin1z_samples[mass_spin_mask]
        spin2z_samples = spin2z_samples[mass_spin_mask]
        mu1_samples = mu1_samples[mass_spin_mask]
        mu2_samples = mu2_samples[mass_spin_mask]
        q_samples = q_samples[mass_spin_mask]

        mc_samples, eta_samples = amrlib.transform_m1m2_mceta(
            m1_samples, m2_samples
        )
        chi_eff_samples, chi_a_samples = amrlib.transform_s1zs2z_chi_eff_chi_a(
            m1_samples,
            m2_samples,
            spin1z_samples,
            spin2z_samples,
        )
        mu1mu2qs2z_prior = uniform_m1m2chi1chi2_prior_to_mu1mu2qchi2(
            mu1_samples, mu2_samples, q_samples, spin2z_samples
        )
        sample_dict["mu1"] = mu1_samples
        sample_dict["mu2"] = mu2_samples
        sample_dict["q"] = q_samples
        sample_dict["spin2z"] = spin2z_samples
        sample_dict["spin1z"] = spin1z_samples
        sample_dict["chi_eff"] = chi_eff_samples
        sample_dict["chi_a"] = chi_a_samples
        sample_dict["mass1"] = m1_samples
        sample_dict["mass2"] = m2_samples
        sample_dict["mchirp"] = mc_samples
        sample_dict["eta"] = eta_samples
        sample_dict["mu1mu2qs2z_prior"] = mu1mu2qs2z_prior
    return sample_dict


def plot_posterior(sample_dict, param, distance_coordinate, grid_level=None):
    print(f"plotting posterior for {param} at grid_level={grid_level}")
    samples = sample_dict[param]
    print(
        f"min({param}_samples)={np.min(samples)}, "
        f"max({param}_samples)={np.max(samples)}"
    )
    if distance_coordinate == "mchirp_eta":
        prior = sample_dict["mceta_prior"]
    elif distance_coordinate == "tau0_tau3":
        prior = sample_dict["tau0tau3_prior"]
    elif distance_coordinate == "mass1_mass2":
        prior = np.ones(len(samples))
    elif distance_coordinate == "mchirp_q":
        prior = sample_dict["mcq_prior"]
    elif distance_coordinate == "mu1_mu2_q_s2z":
        prior = sample_dict["mu1mu2qs2z_prior"]
    fig, ax = plt.subplots()
    ax.hist(
        samples,
        bins=50,
        weights=prior,
        histtype="step",
        density=True,
        color="g",
    )
    ax.axvline(x=inj_param_dict[param], color="blue")
    ax.set_xlabel(param)
    ax.set_ylabel("posterior")
    ax.yaxis.set_ticks([])
    if grid_level is not None:
        plt.title("grid_level = " + str(grid_level))
        filename = (
            f"{output_dir}/summary_plots/posterior_"
            f"{param}_iteration-{str(grid_level)}.png"
        )
    else:
        plt.title("all grids")
        filename = f"{output_dir}/summary_plots/posterior_{param}_all.png"
    plt.savefig(filename)
    return


def plot_2d_posterior_with_grid(sample_dict, param1, param2, grid_level=None):
    if grid_level is not None:
        grid_inds = np.where(np.array(grid_id) == grid_level)[0]
        data1 = intrinsic_param_dict[param1][grid_inds]
        data2 = intrinsic_param_dict[param2][grid_inds]
        weight = margL[grid_inds]
        print(f"min({param1}) = {np.min(data1)}, max({param1}) = {np.max(data1)}")
        print(f"min({param2}) = {np.min(data2)}, max({param2}) = {np.max(data2)}")
    else:
        data1 = intrinsic_param_dict[param1]
        data2 = intrinsic_param_dict[param2]
        weight = margL
        print(f"min({param1}) = {np.min(data1)}, max({param1}) = {np.max(data1)}")
        print(f"min({param2}) = {np.min(data2)}, max({param2}) = {np.max(data2)}")
    plt.figure()
    plt.scatter(data1, data2, c=weight)
    plt.plot(inj_param_dict[param1], inj_param_dict[param2], "r*")
    plt.xlabel(param1)
    plt.ylabel(param2)
    plt.colorbar(label=r"$ln(L_{marg})$")

    samples1 = sample_dict[param1]
    samples2 = sample_dict[param2]
    if param1 == "mchirp" and param1 == "eta":
        prior = sample_dict["mceta_prior"]
    elif param1 == "tau0" and param2 == "tau3":
        prior = sample_dict["tau0tau3_prior"]
    elif param1 == "mass1" and param2 == "mass2":
        prior = np.ones(len(samples1))
    fig, ax = plt.subplots()
    ax.hist2d(samples1, samples2, bins=50, weights=prior, density=True)
    ax.plot(inj_param_dict[param1], inj_param_dict[param2], color="blue")
    ax.set_xlabel(param1)
    ax.set_ylabel(param2)
    if grid_level is not None:
        ax.set_title("grid_level = ", str(grid_level))
        filename = (
            f"{output_dir}/summary_plots/{param1}_{param2}"
            f" _iteration-{str(grid_level)}.png"
        )
    else:
        ax.set_title("all grids")
        filename = (
            output_dir + "/summary_plots/" + param1 + "_" + param2 + "_all.png"
        )
    plt.savefig(filename)
    return


def save_m1m2_posterior_samples(sample_dict, grid_level=None):
    print("saving poserior samples for m1-m2")
    samples_mass1 = sample_dict["mass1"]
    samples_mass2 = sample_dict["mass2"]

    filename = output_dir + "/summary_plots/posterior_samples_all.h5"
    f = h5py.File(filename, "w")
    f.create_dataset("mass1_d", data=samples_mass1)
    f.create_dataset("mass2_d", data=samples_mass2)
    f.close()
    return


params_for_posterior = intrinsic_param[0:2]
print(f"params_for_posterior are {params_for_posterior}")
sample_dict = get_posterior_samples_for_m1m2(intrinsic_param_str)

if intrinsic_param_str in [
    "mass1_mass2",
    "mchirp_eta",
    "tau0_tau3",
    "mchirp_q",
]:
    plot_posterior(
        sample_dict, "mass1", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "mass2", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "mchirp", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(sample_dict, "eta", distance_coordinate=intrinsic_param_str)
    if "tau0" in params_for_posterior:
        plot_posterior(
            sample_dict, "tau0", distance_coordinate=intrinsic_param_str
        )
        plot_posterior(
            sample_dict, "tau3", distance_coordinate=intrinsic_param_str
        )
    if intrinsic_param_str == "mchirp_q":
        plot_posterior(
            sample_dict, "q", distance_coordinate=intrinsic_param_str
        )
    if spin1z_inj is not None:
        plot_posterior(
            sample_dict, "spin1z", distance_coordinate=intrinsic_param_str
        )
        plot_posterior(
            sample_dict, "spin2z", distance_coordinate=intrinsic_param_str
        )
        plot_posterior(
            sample_dict, "chi_eff", distance_coordinate=intrinsic_param_str
        )
        plot_posterior(
            sample_dict, "chi_a", distance_coordinate=intrinsic_param_str
        )
elif intrinsic_param_str == "mu1_mu2_q_s2z":
    plot_posterior(sample_dict, "mu1", distance_coordinate=intrinsic_param_str)
    plot_posterior(sample_dict, "mu2", distance_coordinate=intrinsic_param_str)
    plot_posterior(
        sample_dict, "spin1z", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "spin2z", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "chi_eff", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "chi_a", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(sample_dict, "q", distance_coordinate=intrinsic_param_str)
    plot_posterior(
        sample_dict, "mass1", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "mass2", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(
        sample_dict, "mchirp", distance_coordinate=intrinsic_param_str
    )
    plot_posterior(sample_dict, "eta", distance_coordinate=intrinsic_param_str)

save_m1m2_posterior_samples(sample_dict, grid_level=None)

print(f"All plots saved in {output_dir}")
