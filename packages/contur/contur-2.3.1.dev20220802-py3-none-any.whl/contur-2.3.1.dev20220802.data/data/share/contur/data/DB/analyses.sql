
PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

-- Table for known/allowed beam configurations
-- Assumed to be colliding beams of effctively massless particles (so will need attention if we include fixed target)
-------------------------------------------------------------------------
CREATE TABLE beams (
    id      TEXT NOT NULL UNIQUE,
    collider TEXT NOT NULL,
    particle_a TEXT NOT NULL,
    particle_b TEXT NOT NULL,
    energy_a REAL NOT NULL,
    energy_b REAL NOT NULL,
    PRIMARY KEY(id)
);
INSERT INTO beams VALUES('7TeV','LHC','p+','p+',3500,3500);
INSERT INTO beams VALUES('8TeV','LHC','p+','p+',4000,4000);
INSERT INTO beams VALUES('13TeV','LHC','p+','p+',6500,6500);
-- INSERT INTO beams VALUES('em_27_p_920'); -- positron beam mode to be added for ZEUS analysis
-- INSERT INTO beams VALUES('ep_27_p_820');
-- LEP collider
INSERT INTO beams VALUES('em_ep_91_2','LEP','e+','e-',45.6,45.6);
-- INSERT INTO beams VALUES('pm_pp_1960'); -- Tevatron collider


-- Analysis pools (independent beam/experiment/final state configurations
-------------------------------------------------------------------------
CREATE TABLE analysis_pool (
    pool    TEXT NOT NULL UNIQUE,
    beam    TEXT,
    description TEXT,
    PRIMARY KEY(pool),
    FOREIGN KEY(beam) REFERENCES beams(id)
);

--same sign leptons + missing energy
INSERT INTO analysis_pool VALUES('ATLAS_13_SSLLMET','13TeV','two same-sign leptons(e/mu) plus missing energy jets');

-- all-hadronic inclusive measurements
INSERT INTO analysis_pool VALUES('ATLAS_7_JETS','7TeV','Inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('CMS_7_JETS','7TeV','Inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('ATLAS_8_JETS','8TeV','Inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('CMS_8_JETS','8TeV','Inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('ATLAS_13_JETS','13TeV','Inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('CMS_13_JETS','13TeV','Inclusive hadronic final states');

-- ALICE_2012_I944757 (charm production) good cross section but can't really use without
-- the theory prediction, since the theory uncertainties are vastly bigger than expt.

-- all-hadronic on top pole
INSERT INTO analysis_pool VALUES('ATLAS_13_TTHAD','13TeV','Fully hadronic top events');
INSERT INTO analysis_pool VALUES('CMS_13_TTHAD','13TeV','Fully hadronic top events');
 
-- inclusive isolated photons
INSERT INTO analysis_pool VALUES('ATLAS_7_GAMMA','7TeV','Inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('CMS_7_GAMMA','7TeV','Inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('ATLAS_8_GAMMA','8TeV','Inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('CMS_8_GAMMA','8TeV','Inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('ATLAS_13_GAMMA','13TeV','Inclusive (multi)photons');

-- dileptons below Z pole
INSERT INTO analysis_pool VALUES('ATLAS_7_LMDY','7TeV','Dileptons below the Z pole');

-- dileptons (+jets) on Z pole
INSERT INTO analysis_pool VALUES('ATLAS_7_EEJET','7TeV','e+e- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('ATLAS_7_MMJET','7TeV','mu+mu- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_7_LLJET','7TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_7_EEJET','7TeV','e+e- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('LHCB_7_EEJET','7TeV','e+e- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('LHCB_7_MMJET','7TeV','mu+mu- at the Z pole, plus optional jets');

INSERT INTO analysis_pool VALUES('ATLAS_8_LLJET','8TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('ATLAS_8_EEJET','8TeV','e+e- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('ATLAS_8_MMJET','8TeV','mu+mu- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_8_LLJET','8TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_8_MMJET','8TeV','dimuons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('LHCB_8_MMJET','8TeV','mu+mu- at the Z pole, plus optional jets');

INSERT INTO analysis_pool VALUES('ATLAS_13_EEJET','13TeV','e+e- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('ATLAS_13_MMJET','13TeV','mu+mu- at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('ATLAS_13_LLJET','13TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_13_EEJET','13TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_13_MMJET','13TeV','dileptons at the Z pole, plus optional jets');

-- dileptons (+optional jets) above Z pole
INSERT INTO analysis_pool VALUES('ATLAS_7_HMDY','7TeV','Dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('ATLAS_8_HMDY_EL','8TeV','Dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('ATLAS_8_HMDY_MU','8TeV','Dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('ATLAS_13_HMDY','13TeV','Dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('CMS_13_HMDY','13TeV','Dileptons above the Z pole');

-- three leptons
INSERT INTO analysis_pool VALUES('ATLAS_8_3L','8TeV','trileptons');
INSERT INTO analysis_pool VALUES('CMS_8_3L','8TeV','trileptons');
INSERT INTO analysis_pool VALUES('ATLAS_13_3L','13TeV','trileptons');

-- four leptons
INSERT INTO analysis_pool VALUES('ATLAS_7_4L','7TeV','four leptons');
INSERT INTO analysis_pool VALUES('ATLAS_8_4L','8TeV','four leptons');
INSERT INTO analysis_pool VALUES('ATLAS_13_4L','13TeV','four leptons');

INSERT INTO analysis_pool VALUES('ATLAS_7_LLMET','7TeV','dilepton+MET');

-- three leptons(WZ) + MET  and two leptons with two JETs (WW)

INSERT INTO analysis_pool VALUES('CMS_13_3LJET','13TeV','dileptons or trileptons + MET');

-- two leptons plus gamma
INSERT INTO analysis_pool VALUES('ATLAS_7_EE_GAMMA','7TeV','e+e- plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_7_MM_GAMMA','7TeV','mu+mu- plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_8_EE_GAMMA','8TeV','e+e- plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_8_MM_GAMMA','8TeV','mu+mu- plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_8_LL_GAMMA','8TeV','l+l- plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_13_LL_GAMMA','13TeV','dilepton plus photon');
INSERT INTO analysis_pool VALUES('CMS_7_MM_GAMMA','7TeV','dimuon plus photon');


-- lepton, MET (+optional jets)
INSERT INTO analysis_pool VALUES('ATLAS_7_LMETJET','7TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_7_EMETJET','7TeV','electron, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_7_MMETJET','7TeV','muon, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_7_EMETJET','7TeV','electron, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_7_MMETJET','7TeV','muon, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_8_LMETJET','8TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_8_MMETJET','8TeV','muon, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_8_EMETJET','8TeV','electron, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_8_MMETJET','8TeV','muon, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_8_LMETJET','8TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_13_LMETJET','13TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_13_MMETJET','13TeV','muon, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_13_LMETJET','13TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');

INSERT INTO analysis_pool VALUES('LHCB_8_MJET','8TeV','muons (aimed at W');


-- lepton, met, gamma
INSERT INTO analysis_pool VALUES('ATLAS_7_MMET_GAMMA','7TeV','muon, missing transverse momentum, plus photon');
INSERT INTO analysis_pool VALUES('ATLAS_7_EMET_GAMMA','7TeV','electron, missing transverse momentum, plus photon');
INSERT INTO analysis_pool VALUES('ATLAS_13_LMET_GAMMA','13TeV','semileptonic ttbar+gamma');
INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2MET_GAMMA','13TeV','fully leptonic ttbar+gamma');

-- dilepton (non-resonant), met
INSERT INTO analysis_pool VALUES('ATLAS_7_L1L2MET','7TeV','WW analyses in dilepton plus missing transverse momentum channel');
INSERT INTO analysis_pool VALUES('ATLAS_8_L1L2MET','8TeV','WW analyses in dilepton plus missing transverse momentum channel');
INSERT INTO analysis_pool VALUES('CMS_8_L1L2MET','8TeV','WW analyses in dilepton plus missing transverse momentum channel');
INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2MET','13TeV','unlike dilepton plus missing transverse momentum channel, with jet veto');
INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2METJET','13TeV','unlike dilepton plus missing transverse momentum and jets');

-- dilepton, jet
INSERT INTO analysis_pool VALUES('CMS_13_LLJET','13TeV','WW analyses in dilepton plus zero or one jet');

-- dilepton+b
INSERT INTO analysis_pool VALUES('LHCB_13_L1L2B','13TeV','top pairs via e mu plus b');

-- gamma plus MET
INSERT INTO analysis_pool VALUES('ATLAS_8_GAMMA_MET','8TeV','photon plus missing transverse momentum');
INSERT INTO analysis_pool VALUES('ATLAS_13_GAMMA_MET','13TeV','photon plus missing transverse momentum');

-- hadrons plus MET
INSERT INTO analysis_pool VALUES('ATLAS_13_METJET','13TeV','missing transverse momentum plus jets');
INSERT INTO analysis_pool VALUES('CMS_13_METJET','13TeV','missing transverse momentum plus jets');


-- track based minimum biased
INSERT INTO analysis_pool VALUES('ATLAS_13_TRA','13TeV','track based events');


-- OTHER BEAMS

-- HERA
-- NC DIS inclusive dijets
-- INSERT INTO analysis_pool VALUES('ZEUS_em_27_5_p_920_DJETS', 'em_27_5_p_920','single and double differential inclusive dijet cross sections in NC DIS of em_p beam');
-- INSERT INTO analysis_pool VALUES('ZEUS_ep_27.5_p_920_DJETS', 'ep_27.5_p_920','single and double differential inclusive dijet cross sections in NC DIS of ep_p beam');

-- NC DIS transverse energy flow 
-- INSERT INTO analysis_pool VALUES('H1_ep_27_5_p_820_TE', 'ep_27_5_p_820', 'transverse energy');

-- LEP
-- Hadronic Z decay in EE collisions
-- INSERT INTO analysis_pool VALUES('DELPHI_em_ep_91_2_LLJET', 'em_ep_91_2', 'hadronic z decay to two leptons');
INSERT INTO analysis_pool VALUES('OPAL_912_JETS', 'em_ep_91_2', 'z decay to multiple hadronic final states');
INSERT INTO analysis_pool VALUES('OPAL_912_JETS_GAMMA', 'em_ep_91_2', 'z decay to hadronic and photon final states');
-- INSERT INTO analysis_pool VALUES('ALEPH_em_ep_91_2_JETS', 'em_ep_91_2', 'z decay to multiple hadronic final states');
-- INSERT INTO analysis_pool VALUES('L3_em_ep_91_2_JETS', 'em_ep_91_2', 'z decay to multiple hadronic final states');

-- TEVATRON
-- dilepton
-- INSERT INTO analysis_pool VALUES('D0_pm_pp_1960_L1L2', 'pm_pp_1960', 'z_star and gamma to dilepton production');



-- Now the actual analyses, assigning them to pools
-------------------------------------------------------------------------
-- id: is the uninque identifier of the analysis, including any options strings.
-- lumi: gives the intergrated luminosity units which the rivet plots are normalised to. Note that if the value given here is
-- parseable as a number, it will override the lumi in the rivet info file. If so, it should always match the units of the cross section
-- plots, or be 1 for event count plots.
-- pool: the analysis pool this is assigned to.

CREATE TABLE analysis (
    id      TEXT NOT NULL UNIQUE,
    lumi    TEXT,
    pool    TEXT,
    PRIMARY KEY(id),
    FOREIGN KEY(pool) REFERENCES analysis_pool(pool)
);


----------------------------------

-- Superseded/deprecated analyses
-- INSERT INTO analysis VALUES('ATLAS_2012_I1083318','pb',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_I945498','pb',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_I921594','pb',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_S9128077','pb',NULL);

-- 7 TeV fully hadronic
INSERT INTO analysis VALUES('ATLAS_2014_I1325553','pb','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1268975','pb','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1326641','pb','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1307243','pb','ATLAS_7_JETS');
INSERT INTO analysis VALUES('CMS_2014_I1298810','pb','CMS_7_JETS');
INSERT INTO analysis VALUES('CMS_2013_I1273574','pb','CMS_7_JETS');
INSERT INTO analysis VALUES('CMS_2013_I1208923','pb','CMS_7_JETS');
INSERT INTO analysis VALUES('CMS_2012_I1089835','pb','CMS_7_JETS');

-- 7 TeV photons
INSERT INTO analysis VALUES('ATLAS_2012_I1093738','pb','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1244522','pb','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1263495','pb','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2012_I1199269','pb','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('CMS_2014_I1266056','pb','CMS_7_GAMMA');

-- 7 TeV high mass Drell Yan
INSERT INTO analysis VALUES('ATLAS_2013_I1234228','pb','ATLAS_7_HMDY');


-- 7 TeV Z+jets
INSERT INTO analysis VALUES('ATLAS_2013_I1230812:LMODE=EL','pb','ATLAS_7_EEJET');
INSERT INTO analysis VALUES('ATLAS_2013_I1230812:LMODE=MU','pb','ATLAS_7_MMJET');
INSERT INTO analysis VALUES('ATLAS_2014_I1306294:LMODE=EL','pb','ATLAS_7_EEJET');
INSERT INTO analysis VALUES('ATLAS_2014_I1306294:LMODE=MU','pb','ATLAS_7_MMJET');
INSERT INTO analysis VALUES('CMS_2015_I1310737','pb','CMS_7_LLJET');
INSERT INTO analysis VALUES('LHCB_2014_I1262703','pb','LHCB_7_MMJET');
-- 7 TeV inclusive Z
INSERT INTO analysis VALUES('ATLAS_2016_I1502620:LMODE=ZEL','pb','ATLAS_7_EEJET');
INSERT INTO analysis VALUES('ATLAS_2016_I1502620:LMODE=ZMU','pb','ATLAS_7_MMJET');
INSERT INTO analysis VALUES('LHCB_2012_I1208102','pb','LHCB_7_EEJET');

-- 7 TeV ttbar --- TODO this can be split into E and MU channels
INSERT INTO analysis VALUES('ATLAS_2015_I1345452','pb','ATLAS_7_LMETJET');

-- 7 TeV Low mass DY
INSERT INTO analysis VALUES('ATLAS_2014_I1288706','pb','ATLAS_7_LMDY');

-- 7 TeV single jet masses: The rivet routines actually use only electrons, even though
-- the measurement used muons too. Not very confident about the normalisation.
INSERT INTO analysis VALUES('CMS_2013_I1224539:JMODE=W','fb','CMS_7_EMETJET');
INSERT INTO analysis VALUES('CMS_2013_I1224539:JMODE=Z','fb','CMS_7_EEJET');

-- 7 TeV W+jets.
INSERT INTO analysis VALUES('ATLAS_2016_I1502620:LMODE=WEL','pb','ATLAS_7_EMETJET');
INSERT INTO analysis VALUES('ATLAS_2016_I1502620:LMODE=WMU','pb','ATLAS_7_MMETJET');
INSERT INTO analysis VALUES('ATLAS_2014_I1319490:LMODE=MU','pb','ATLAS_7_MMETJET');
INSERT INTO analysis VALUES('ATLAS_2014_I1319490:LMODE=EL','pb','ATLAS_7_EMETJET');
INSERT INTO analysis VALUES('CMS_2014_I1303894','pb','CMS_7_MMETJET');

-- 7 TeV W+charm
INSERT INTO analysis VALUES('ATLAS_2014_I1282447','pb','ATLAS_7_LMETJET');

-- 7 TeV W+b
INSERT INTO analysis VALUES('ATLAS_2013_I1219109:LMODE=EL','fb','ATLAS_7_EMETJET'); --W plus b jets
INSERT INTO analysis VALUES('ATLAS_2013_I1219109:LMODE=MU','fb','ATLAS_7_MMETJET'); --W plus b jets

-- 7 TeV Z+bb
INSERT INTO analysis VALUES('CMS_2013_I1256943','pb','CMS_7_LLJET');

-- 7 TeV WW. Plots in fb.
INSERT INTO analysis VALUES('ATLAS_2013_I1190187','fb','ATLAS_7_L1L2MET'); -- jet veto is correctly applied in fiducial cuts.

-- 7 TeV dibosons, plots in fb
INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=ZEL','fb','ATLAS_7_EE_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=ZMU','fb','ATLAS_7_MM_GAMMA');
INSERT INTO analysis VALUES('CMS_2015_I1346843','fb','CMS_7_MM_GAMMA');

INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=WEL','fb','ATLAS_7_EMET_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=WMU','fb','ATLAS_7_MMET_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2012_I1203852:LMODE=LL','fb','ATLAS_7_4L');
INSERT INTO analysis VALUES('ATLAS_2012_I1203852:LMODE=LNU','fb','ATLAS_7_LLMET');

-- 8 TeV fully hadronic
-- plots in fb
INSERT INTO analysis VALUES('ATLAS_2015_I1394679','fb','ATLAS_8_JETS');
INSERT INTO analysis VALUES('ATLAS_2017_I1598613:BMODE=3MU','fb','ATLAS_8_JETS');
-- for the b hadron mode
-- plots in pb
INSERT INTO analysis VALUES('ATLAS_2017_I1604271','pb','ATLAS_8_JETS');
INSERT INTO analysis VALUES('CMS_2016_I1487277','pb','CMS_8_JETS');
INSERT INTO analysis VALUES('CMS_2017_I1598460','pb','CMS_8_JETS'); -- triple differential dijets

-- normalised, no total xsec yet INSERT INTO analysis VALUES('CMS_2016_I1421646',19700,'CMS_8_JETS');

-- 8 TeV photons
-- in pb
INSERT INTO analysis VALUES('ATLAS_2016_I1457605','pb','ATLAS_8_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2017_I1632756','pb','ATLAS_8_GAMMA'); -- +hf
-- in fb
INSERT INTO analysis VALUES('ATLAS_2017_I1591327','fb','ATLAS_8_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2014_I1306615','fb','ATLAS_8_GAMMA'); -- higgs to photons
INSERT INTO analysis VALUES('ATLAS_2017_I1644367','fb','ATLAS_8_GAMMA'); -- 3gamma (fb)


-- 8 TeV High mass DY
-- in pb
INSERT INTO analysis VALUES('ATLAS_2016_I1467454:LMODE=EL','pb','ATLAS_8_HMDY_EL');
INSERT INTO analysis VALUES('ATLAS_2016_I1467454:LMODE=MU','pb','ATLAS_8_HMDY_MU');

-- 8 TeV leptons+MET, dileptons

-- normalised
INSERT INTO analysis VALUES('ATLAS_2014_I1279489','pb','ATLAS_8_LLJET'); -- electroweak Z+jets
INSERT INTO analysis VALUES('ATLAS_2015_I1408516:LMODE=EL','pb','ATLAS_8_EEJET'); -- Z production
INSERT INTO analysis VALUES('ATLAS_2015_I1408516:LMODE=MU','pb','ATLAS_8_MMJET'); -- Z production
INSERT INTO analysis VALUES('ATLAS_2019_I1744201','fb','ATLAS_8_EEJET'); -- Z+jets
INSERT INTO analysis VALUES('CMS_2016_I1471281:VMODE=Z','fb','CMS_8_MMJET'); -- Z pT
INSERT INTO analysis VALUES('CMS_2016_I1471281:VMODE=W','fb','CMS_8_LMETJET'); -- W pT

-- plots in pb
INSERT INTO analysis VALUES('ATLAS_2017_I1589844:LMODE=EL','pb','ATLAS_8_EEJET');
INSERT INTO analysis VALUES('ATLAS_2017_I1589844:LMODE=MU','pb','ATLAS_8_MMJET');
INSERT INTO analysis VALUES('CMS_2017_I1499471','pb','CMS_8_LLJET');
INSERT INTO analysis VALUES('CMS_2016_I1491953','pb','CMS_8_MMETJET');
INSERT INTO analysis VALUES('ATLAS_2015_I1404878','pb','ATLAS_8_LMETJET');


INSERT INTO analysis VALUES('LHCB_2016_I1454404:MODE=WJET','fb','LHCB_8_MJET');
INSERT INTO analysis VALUES('LHCB_2016_I1454404:MODE=ZJET','fb','LHCB_8_MMJET');

-- ATLAS_2016_I1487726: collinear Wj at 8 TeV Cross sections, but the theory uncertainty is too large
-- to use it without the having the theory prediction

-- plots in fb
INSERT INTO analysis VALUES('CMS_2016_I1454211','fb','CMS_8_LMETJET'); -- NB partonic phase space?
INSERT INTO analysis VALUES('ATLAS_2015_I1397637','fb','ATLAS_8_LMETJET'); -- ttbar
INSERT INTO analysis VALUES('ATLAS_2017_I1517194:LMODE=EL','fb','ATLAS_8_EMETJET'); -- electroweak W+jets
INSERT INTO analysis VALUES('ATLAS_2017_I1517194:LMODE=MU','fb','ATLAS_8_MMETJET'); -- electroweak W+jets
INSERT INTO analysis VALUES('ATLAS_2018_I1635273:LMODE=EL','fb','ATLAS_8_EMETJET'); -- W+jets. NB some plots in pb
INSERT INTO analysis VALUES('ATLAS_2018_I1635273:LMODE=MU','fb','ATLAS_8_MMETJET'); -- W+jets NB some plots in pb


-- plots in fb
INSERT INTO analysis VALUES('CMS_2017_I1518399','fb','CMS_8_LMETJET');  -- TTBAR
INSERT INTO analysis VALUES('ATLAS_2016_I1426515','fb','ATLAS_8_L1L2MET'); -- nb jet veto is implemented in fiducial cuts.
INSERT INTO analysis VALUES('CMS_2017_I1467451','fb','CMS_8_L1L2MET'); -- nb b-jet veto is NOT implemented in fiducial cuts; and large data driven bg subtraction.

-- fb
INSERT INTO analysis VALUES('ATLAS_2015_I1394865','fb','ATLAS_8_4L');
INSERT INTO analysis VALUES('ATLAS_2014_I1310835','fb','ATLAS_8_4L');
INSERT INTO analysis VALUES('ATLAS_2016_I1448301:LMODE=MU','fb','ATLAS_8_MM_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2016_I1448301:LMODE=EL','fb','ATLAS_8_EE_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2016_I1448301:LMODE=LL','fb','ATLAS_8_LL_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2016_I1448301:LMODE=NU','fb','ATLAS_8_GAMMA_MET');
INSERT INTO analysis VALUES('ATLAS_2016_I1492320:LMODE=3L','fb','ATLAS_8_3L');
INSERT INTO analysis VALUES('ATLAS_2016_I1492320:LMODE=2L2J','fb','ATLAS_8_L1L2MET'); -- nb b-jet veto IS implemented in fiducial cuts
INSERT INTO analysis VALUES('ATLAS_2016_I1444991','fb','ATLAS_8_L1L2MET'); -- nb jet veto IS implemented in fiducial cuts; but large data-driven top subtraction

INSERT INTO analysis VALUES('CMS_2016_I1487288','fb','CMS_8_3L');

-- 13 TeV DY. 
INSERT INTO analysis VALUES('ATLAS_2019_I1725190','eventcount','ATLAS_13_HMDY'); -- lumi is set in routine, to give event counts
INSERT INTO analysis VALUES('CMS_2018_I1711625','pb','CMS_13_HMDY');    -- plots in pb

-- 13 TeV fully hadronic
INSERT INTO analysis VALUES('ATLAS_2018_I1634970','pb','ATLAS_13_JETS');
INSERT INTO analysis VALUES('ATLAS_2019_I1724098','pb','ATLAS_13_JETS'); -- jet substructure.
INSERT INTO analysis VALUES('ATLAS_2017_I1637587','pb','ATLAS_13_JETS'); -- soft drop jet mass
INSERT INTO analysis VALUES('ATLAS_2020_I1808726','fb','ATLAS_13_JETS');  -- multijet event shapes
INSERT INTO analysis VALUES('CMS_2019_I1753720','pb','CMS_13_TTHAD'); -- all-jet top events with b-jets.
INSERT INTO analysis VALUES('CMS_2021_I1932460','pb','CMS_13_JETS');
INSERT INTO analysis VALUES('CMS_2021_I1847230:MODE=QCD13TeV','2.3','CMS_13_JETS'); -- 13TeV mode three jets
INSERT INTO analysis VALUES('CMS_2021_I1847230:MODE=QCD8TeV','19.8','CMS_8_JETS'); -- 8TeV mode three jets

-- INSERT INTO analysis VALUES('ATLAS_2019_I1772062',32900.0,'ATLAS_13_JETS'); -- soft drop variables
-- (not really suitable, at least without more work. normalisation not provided, and theory uncertainties large)

INSERT INTO analysis VALUES('CMS_2016_I1459051','pb','CMS_13_JETS');
INSERT INTO analysis VALUES('CMS_2018_I1682495','pb','CMS_13_JETS'); -- jet mass

-- 13 TeV dileptons+jets
-- plots in pb
INSERT INTO analysis VALUES('ATLAS_2017_I1514251:LMODE=EL','pb','ATLAS_13_EEJET'); -- Z+jets
INSERT INTO analysis VALUES('ATLAS_2017_I1514251:LMODE=MU','pb','ATLAS_13_MMJET'); -- Z+jets
INSERT INTO analysis VALUES('CMS_2018_I1667854:LMODE=EL','pb','CMS_13_EEJET'); -- Z+jets
INSERT INTO analysis VALUES('CMS_2018_I1667854:LMODE=MU','pb','CMS_13_MMJET'); -- Z+jets
INSERT INTO analysis VALUES('CMS_2019_I1753680:LMODE=EL','pb','CMS_13_EEJET'); -- Z production
INSERT INTO analysis VALUES('CMS_2019_I1753680:LMODE=MU','pb','CMS_13_MMJET'); -- Z production
INSERT INTO analysis VALUES('ATLAS_2020_I1788444:LMODE=EL','pb','ATLAS_13_EEJET'); -- Z+bb
INSERT INTO analysis VALUES('ATLAS_2020_I1788444:LMODE=MU','pb','ATLAS_13_MMJET'); -- Z+bb
INSERT INTO analysis VALUES('ATLAS_2020_I1803608','fb','ATLAS_13_LLJET'); -- Electroweak Z+jets
INSERT INTO analysis VALUES('CMS_2020_I1814328','pb','CMS_13_LLJET'); -- WW -> 2l with one or zero jet
INSERT INTO analysis VALUES('ATLAS_2019_I1768911','pb','ATLAS_13_LLJET'); -- plots in pb


INSERT INTO analysis VALUES('CMS_2021_I1847230:MODE=ZJet','19.8','CMS_8_MMJET');-- Z (dimuons) + jets in ZJet mode need to be careful when using these histos! Normalisation factors are uncertain. 



-- plot in fb
INSERT INTO analysis VALUES('ATLAS_2019_I1738841','fb','ATLAS_13_SSLLMET'); -- Electroweak same sign WW -> 2l at least 2 jets


-- 13 TeV leptons+MET
INSERT INTO analysis VALUES('CMS_2017_I1610623','pb','CMS_13_MMETJET'); -- W+jets
INSERT INTO analysis VALUES('CMS_2016_I1491950','pb','CMS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('CMS_2018_I1662081','pb','CMS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('CMS_2018_I1663958','pb','CMS_13_LMETJET'); -- ttbar+jets (pb)
INSERT INTO analysis VALUES('CMS_2019_I1705068','pb','CMS_13_MMETJET'); -- W+charm
INSERT INTO analysis VALUES('CMS_2019_I1744604','pb','CMS_13_LMETJET'); -- single top

-- 13 TeV photon + MET
INSERT INTO analysis VALUES('ATLAS_2018_I1698006:LVETO=ON','fb','ATLAS_13_GAMMA_MET');

INSERT INTO analysis VALUES('ATLAS_2017_I1614149','pb','ATLAS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('ATLAS_2019_I1750330:TYPE=BOTH','pb','ATLAS_13_LMETJET'); --ttbar

INSERT INTO analysis VALUES('LHCB_2018_I1662483','fb','LHCB_13_L1L2B'); --ttbar

INSERT INTO analysis VALUES('ATLAS_2017_I1625109','fb','ATLAS_13_4L');  -- ZZ
INSERT INTO analysis VALUES('ATLAS_2019_I1720442','fb','ATLAS_13_4L');  -- inclusive
INSERT INTO analysis VALUES('ATLAS_2021_I1849535','fb','ATLAS_13_4L');  -- inclusive


-- Various BG regions from LQ search. plots in pb
INSERT INTO analysis VALUES('ATLAS_2019_I1718132:LMODE=ELMU','pb','ATLAS_13_L1L2METJET');
INSERT INTO analysis VALUES('ATLAS_2019_I1718132:LMODE=ELEL','pb','ATLAS_13_EEJET');
INSERT INTO analysis VALUES('ATLAS_2019_I1718132:LMODE=MUMU','pb','ATLAS_13_MMJET');
INSERT INTO analysis VALUES('ATLAS_2018_I1656578','fb','ATLAS_13_LMETJET'); --Top + jets
INSERT INTO analysis VALUES('ATLAS_2018_I1705857','fb','ATLAS_13_LMETJET'); --Top + b jets (normalised)

-- 13 TeV MET+JET
INSERT INTO analysis VALUES('ATLAS_2017_I1609448','pb','ATLAS_13_METJET'); -- HAVE THEORY
INSERT INTO analysis VALUES('ATLAS_2016_I1458270','eventcount','ATLAS_13_METJET'); -- HAVE THEORY. 0l+MET+nJets search. Lumi is set to 3.2 in the routine
-- INSERT INTO analysis VALUES('CMS_2020_I1837084','pb','CMS_13_METJET'); -- CMS z->vv; however, rivet runs only on muons

-- hadronic top
INSERT INTO analysis VALUES('ATLAS_2018_I1646686','pb','ATLAS_13_TTHAD'); -- Hadronic top pairs (pb)
INSERT INTO analysis VALUES('ATLAS_2020_I1801434','pb','ATLAS_13_TTHAD'); -- Hadronic top pairs (pb)
INSERT INTO analysis VALUES('CMS_2019_I1764472','fb','CMS_13_TTHAD'); -- Hadronic top pairs (fb)

INSERT INTO analysis VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','fb','ATLAS_13_LMET_GAMMA'); -- semileptonic ttbar + gamma
INSERT INTO analysis VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','fb','ATLAS_13_L1L2MET_GAMMA'); -- leptonic ttbar + gamma

-- 13 TeV photons
INSERT INTO analysis VALUES('ATLAS_2021_I1887997','pb','ATLAS_13_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2017_I1645627','pb','ATLAS_13_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2019_I1772071','pb','ATLAS_13_GAMMA');

-- 13 TeV photons+ll
INSERT INTO analysis VALUES('ATLAS_2019_I1764342','fb','ATLAS_13_LL_GAMMA'); -- Z+gamma

-- 13 TeV WW production cross-section
INSERT INTO analysis VALUES('ATLAS_2019_I1734263','fb','ATLAS_13_L1L2MET'); -- no jets
INSERT INTO analysis VALUES('ATLAS_2021_I1852328','fb','ATLAS_13_L1L2METJET'); -- with jets

-- 13 TeV leptonic ttbar
INSERT INTO analysis VALUES('ATLAS_2019_I1759875','fb','ATLAS_13_L1L2METJET');

-- dodgy ATLAS 13TeV 3L
INSERT INTO analysis VALUES('ATLAS_2016_I1469071','fb','ATLAS_13_3L');

-- 13 TeV track based minimum biased events, in pb^{-1}
INSERT INTO analysis VALUES('ATLAS_2016_I1419652','ub','ATLAS_13_JETS'); -- 
INSERT INTO analysis VALUES('ATLAS_2016_I1467230','ub','ATLAS_13_JETS'); --  with low pT tracks
INSERT INTO analysis VALUES('ATLAS_2019_I1740909','pb','ATLAS_13_JETS'); --  jet fragmentation using charged particles
INSERT INTO analysis VALUES('ATLAS_2020_I1790256','pb','ATLAS_13_JETS'); --  Lund jet plane with charged particles

--13 TeV WW or WZ production cross-section with three or two leptons
INSERT INTO analysis VALUES('CMS_2020_I1794169','fb','CMS_13_3LJET'); 

-- OTHER BEAMS ANALYSES

-- HERA
-- INSERT INTO analysis VALUES('ZEUS_2010_I875006', 203.0, 'ZEUS_em275_920_DJETS'); -- inclusive diject cross sections (highest Q2 dataset of ep and em data used) 
-- INSERT INTO analysis VALUES('H1_2000_S4129130', 8.2, 'H1_ep27_820_TE'); -- transverse energy flow (using highest Q2 luminosity)

-- LEP Z decays
-- INSERT INTO analysis VALUES('DELPHI_1994_I375963', 0.0405, 'DELPHI_em_ep_91_2_LLJET'); -- dimuons
INSERT INTO analysis VALUES('OPAL_1992_I321190', 'pb', 'OPAL_912_JETS'); -- Charged Particle Multiplicities of hadronic final states
-- INSERT INTO analysis VALUES('ALEPH_2001_I555653', 160, 'ALEPH_em_ep_91_2'); -- tau polarization (lots of different decay modes?)
-- INSERT INTO analysis VALUES('ALEPH_1996_I421984', 132, 'ALEPH_em_ep_91_2_JETS'); -- tau decays with eta and omega mesons
-- INSERT INTO analysis VALUES('L3_1994_I374698', 35, 'L3_em_ep_91_2_JETS'); -- particle identification and multiple decay modes?
-- INSERT INTO analysis VALUES('L3_1997_I427107', 112, 'L3_em_ep_91_2_JETS'); -- eta' and omega meson production rates
-- INSERT INTO analysis VALUES('L3_1998_I467929', 149, 'l3_em_ep_91_2_JETS'); -- multiple different final states?
INSERT INTO analysis VALUES('OPAL_1993_S2692198', 'pb', 'OPAL_912_JETS_GAMMA'); -- photon production from quarks (rivet routine dodgy)
INSERT INTO analysis VALUES('OPAL_1994_S2927284', 'pb', 'OPAL_912_JETS'); -- meson and hadron production rates
-- INSERT INTO analysis VALUES('OPAL_1995_I393503', 45.9, 'OPAL_em_ep_91_2_JETS'); -- K0 particle identification?
-- INSERT INTO analysis VALUES('OPAL_1998_S3780481', 177, 'OPAL_em_ep_91_2_JETS'); -- qqbar fragmentation functions
-- INSERT INTO analysis VALUES('OPAL_2001_I554583', 151, 'OPAL_em_ep_91_2_JETS'); -- tau polarization (lots of decay modes?)

-- TEVATRON
-- INSERT INTO analysis VALUES('D0_2015_I1324946', 10.4, 'D0_pm_pp_1960_L1L2'); -- Zstarandphoton production to two muons, fb-1

-- VARIOUS ANALYSIS WHICH HAVE BEEN CONSIDERED BUT NOT CURRENTLY USED
-- See also the gitlab "new data" tickets.
-- https://gitlab.com/hepcedar/contur/-/issues?scope=all&state=all&label_name[]=New%20data
-- Note that the ones where we don't have normalisation could be used if we had SM theory.
--
-- -------------------------------------------------------------------------------------------------------------------
-- TODO: Why aren't we using these? 
-- -------------------------------------------------------------------------------------------------------------------
-- ATLAS_2017_I1626105  Dileptonic ttbar at 8 TeV
-- ATLAS_2017_I1604029 – ttbar + gamma at 8 TeV

-- -------------------------------------------------------------------------------------------------------------------
-- These ones we can use if we get SM predictions
-- -------------------------------------------------------------------------------------------------------------------
-- INSERT INTO analysis VALUES('CMS_2015_I1370682',  Top quark. Particle-level, but don't have normalisation. Can use if we get SM theory predictions (Maybe from MA?)
-- INSERT INTO analysis VALUES('CMS_2017_I1519995',2600,'CMS_13_JETS'); --  search, with unfolded data. don't have normalisation
-- INSERT INTO analysis VALUES('CMS_2013_I1224539_DIJET',5000.0,'CMS_7_JETS'); 
-- ATLAS_2017_I1495243',3.2,'ATLAS_13_LMETJET'); --Top + jets, but all area normalised sadly, without providing the xsec.
-- CMS_2018_I1690148 jet substr in top ALL NORMALISED, DONT USE
-- CMS_2016_I1421646 – Dijet azimuthal decorrelations in $pp$ collisions at $\sqrt{s} = 8$ TeV (normalised)
-- g->bb ATLAS_2018_I1711114  Would be nice but need normalisation
-- Dileptonic emu tt early cross-section measurement at 13 TeV
-- off-resonance.  ATLAS_2018_I1677498 Would be nice but need normalisation
-- ATLAS_2021_I1913061 b frag  (normalised) https://gitlab.com/hepcedar/contur/-/issues/218

-- -------------------------------------------------------------------------------------------------------------------
-- These are probably not useful here 
-- -------------------------------------------------------------------------------------------------------------------
-- INSERT INTO analysis VALUES('ATLAS_2017_I1598613:BMODE=BB',11.4,'ATLAS_8_JETS'); cant use two modes in same pool. also, we don't have normalisation for this one.
-- INSERT INTO analysis VALUES('CMS_2018_I1686000',1960.0,'CMS_8_3L'); -- huge bg subtraction, BDTs etc.
-- LHCB_2018_I1665223 -- inelastic pp total cross section not really relevant here.
-- CMS_2018_I1708620 -- soft QCD/energy density
-- ALICE_2012_I944757 -- charm in central rapidity region
-- INSERT INTO analysis VALUES('ATLAS_2016_I1468168' Inclusive/extrapolated only. do not use.
-- CMS_2020_I1837084 z->vv and ll. Both measured separately, however, only the muon version is in rivet. There are
--                                 also multiple vetos in the analysis which are not in the fiducial phase space,
--                                 so applicability is limited.
-- ATLAS_2021_I1941095 ttbar asymmetry see https://gitlab.com/hepcedar/contur/-/issues/204



-- Table to store the mapping of a histogram to its covariance matrix
CREATE TABLE covariances (
    id      TEXT NOT NULL UNIQUE,
    cov     TEXT,
    PRIMARY KEY(id)
);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1637587/d01-x01-y01','/REF/ATLAS_2017_I1637587/d10-x01-y01');
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1637587/d02-x01-y01','/REF/ATLAS_2017_I1637587/d11-x01-y01');
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1637587/d03-x01-y01','/REF/ATLAS_2017_I1637587/d12-x01-y01');



-- Histograms in a given analysis which should be ignored.
CREATE TABLE blacklist (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);


-- hadronic top (remove the normalised versions)
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d02-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d06-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d10-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d14-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d18-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d22-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d26-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d30-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d34-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d38-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d42-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d46-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d50-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d54-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d58-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d62-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d66-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d70-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d74-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d78-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d82-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d86-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d90-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d94-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d98-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d102-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d106-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d110-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d114-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d118-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d122-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d126-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d130-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d134-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d139-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d140-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d141-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d142-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d167-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d168-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d169-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d170-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d195-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d196-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d197-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d198-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d223-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d224-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d225-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d226-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d251-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d252-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d253-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d254-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d279-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d280-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d281-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d282-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d307-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d308-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d309-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d310-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d335-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d336-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d337-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d338-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d363-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d364-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d365-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d366-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d391-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d392-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d393-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d394-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d405-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d406-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d407-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d408-x01-y01');

INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d419-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d420-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d421-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2020_I1801434','d422-x01-y01');



-- remove the correlations
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d15');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d16');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d17');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d18');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d19');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d20');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d21');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d22');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d23');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d24');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d25');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d26');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d27');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d28');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d29');
-- remove the theory predictions
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','y02');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','y03');
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','y04');

-- remove the 3D correlations
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','d05');
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','d06');
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','d07');
-- remove theory predictions
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','y02');
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','y03');
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','y04');

-- normalisation blacklisted New WW 2019                                   --------------------------------------------------------
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d22-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d25-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d28-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d31-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d34-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d37-x01-y01');

-- extrapolated to simplified phase space blacklisted New WW 2019

INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d41-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d42-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2019_I1734263','d43-x01-y01');




INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=EL','d02');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=EL','d04');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=EL','d06');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=EL','d08');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=MU','d02');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=MU','d04');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=MU','d06');
INSERT INTO blacklist VALUES('ATLAS_2013_I1230812:LMODE=MU','d08');
-- don't use the normalised plots
INSERT INTO blacklist VALUES('CMS_2013_I1273574','d10');
INSERT INTO blacklist VALUES('CMS_2013_I1273574','d11');
INSERT INTO blacklist VALUES('CMS_2013_I1273574','d12');

INSERT INTO blacklist VALUES('CMS_2014_I1298810','d13');
INSERT INTO blacklist VALUES('CMS_2014_I1298810','d14');
INSERT INTO blacklist VALUES('CMS_2014_I1298810','d15');
INSERT INTO blacklist VALUES('CMS_2014_I1298810','d16');
INSERT INTO blacklist VALUES('CMS_2014_I1298810','d17');
INSERT INTO blacklist VALUES('CMS_2014_I1298810','d18');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=ZEL','d17');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=ZEL','d18');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=ZEL','d20');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=ZMU','d17');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=ZMU','d18');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=ZMU','d20');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=WMU','d15');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=WMU','d16');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=WMU','d19');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=WEL','d15');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=WEL','d16');
INSERT INTO blacklist VALUES('ATLAS_2013_I1217863:LMODE=WEL','d19');
INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d10-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d11-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d12-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d13-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d14-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d15-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2014_I1306615','d29');
INSERT INTO blacklist VALUES('ATLAS_2014_I1306615','d30');
-- ATLAS Z+jets ratios
INSERT INTO blacklist VALUES('ATLAS_2017_I1514251:LMODE=EL','d07-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2017_I1514251:LMODE=MU','d08-x01-y01');

INSERT INTO blacklist VALUES('CMS_2017_I1518399','d02');
INSERT INTO blacklist VALUES('CMS_2016_I1491953','d36');
INSERT INTO blacklist VALUES('CMS_2016_I1491953','d37');
INSERT INTO blacklist VALUES('CMS_2016_I1491953','d38');
INSERT INTO blacklist VALUES('CMS_2016_I1491953','d39');

INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d16');
INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d18');
INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d20');
INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d22');
INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d24');
INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d26');
INSERT INTO blacklist VALUES('ATLAS_2017_I1614149','d28');


-- have to veto all these at the moment because contur doesn't know
-- how to handle weighted differential xsecs presented as a 2D scatter.
INSERT INTO blacklist VALUES('ATLAS_2017_I1598613:BMODE=3MU','d01');

-- remove the normalised versions of the plots from CMS top.
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d42-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d44-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d46-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d48-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d50-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d52-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d54-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d56-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d58-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d59-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d60-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d61-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d63-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d64-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d65-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d66-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d68-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d69-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d70-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d71-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d73-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d74-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d75-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d76-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d78-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d79-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d80-x02-y01');
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d81-x02-y01');
-- CMS Z+b ratios
INSERT INTO blacklist VALUES('CMS_2017_I1499471','d02-x01-y01');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','d04-x01-y01');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','d06-x01-y01');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','d08-x01-y01');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','d10-x01-y01');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','Z_pt');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','Dphi_Zj');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','first_jet');
INSERT INTO blacklist VALUES('CMS_2017_I1499471','HT');

-- ATLAS inclusive W/Z ratios
INSERT INTO blacklist VALUES('ATLAS_2016_I1502620:LMODE=WEL','d35-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2016_I1502620:LMODE=WEL','d35-x01-y02');
INSERT INTO blacklist VALUES('ATLAS_2016_I1502620:LMODE=WMU','d35-x01-y01');
INSERT INTO blacklist VALUES('ATLAS_2016_I1502620:LMODE=WMU','d35-x01-y02');

INSERT INTO blacklist VALUES('CMS_2018_I1662081','d01');
INSERT INTO blacklist VALUES('CMS_2018_I1662081','d02');
INSERT INTO blacklist VALUES('CMS_2018_I1662081','d03');
INSERT INTO blacklist VALUES('CMS_2018_I1662081','d04');
INSERT INTO blacklist VALUES('CMS_2018_I1662081','d05');
INSERT INTO blacklist VALUES('CMS_2018_I1662081','d06');
INSERT INTO blacklist VALUES('CMS_2018_I1662081','d07');

-- CMS jet mass normalised plots.
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d25');
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d26');
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d27');
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d28');
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d29');
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d3');
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d4');

-- BG subtracted tt bb
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d02');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d03');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d04');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d06');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d08');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d10');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d12');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d14');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d16');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d18');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d20');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d22');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d24');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d26');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d28');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d30');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d32');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d34');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d36');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d38');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d40');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d42');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d44');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d46');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d48');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d50');
INSERT INTO blacklist VALUES('ATLAS_2018_I1705857','d52');

INSERT INTO blacklist VALUES('CMS_2018_I1711625','d03'); -- DY extrapolated

-- ATLAS WZ "total cross section"
INSERT INTO blacklist VALUES('ATLAS_2016_I1469071','d06');

-- W+/- ratios
INSERT INTO blacklist VALUES('ATLAS_2018_I1635273:LMODE=EL','y03');
INSERT INTO blacklist VALUES('ATLAS_2018_I1635273:LMODE=MU','y03');

-- pt mass ratio
INSERT INTO blacklist VALUES('ATLAS_2020_I1788444:LMODE=MU','d15');

-- both actual and normalised are produced in the rivet analysis CMS_2021_I1932460, hence blocked normalised plots
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d09-x01-y01');
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d10-x01-y01'); 
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d11-x01-y01');
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d12-x01-y01');
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d13-x01-y01');
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d14-x01-y01');

-- If an analysis has entries here, only the histograms mathcing the enetries will
-- be used, the rest will be ignored.
CREATE TABLE whitelist (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
-- Z->vv
-- INSERT INTO whitelist VALUES('CMS_2020_I1837084','d04-x01-y04');


-- 4L
INSERT INTO whitelist VALUES('ATLAS_2021_I1849535','y01');

-- W charm
INSERT INTO whitelist VALUES('ATLAS_2014_I1282447','d03-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1282447','d04-x01-y03');
--
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d01-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d01-x02-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d02-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d03-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d03-x02-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d04-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d04-x02-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d05-x03-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d05-x04-y01');
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d05-x05-y01');
--
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d13');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d14');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d15');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d16');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d17');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d18');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d19');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d20');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d21');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d22');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d23');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d24');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d25');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d26');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d27');
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d28');
--
INSERT INTO whitelist VALUES('CMS_2016_I1454211','d02');
INSERT INTO whitelist VALUES('CMS_2016_I1454211','d04');
INSERT INTO whitelist VALUES('CMS_2016_I1454211','d06');
INSERT INTO whitelist VALUES('CMS_2016_I1454211','d08');
--
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d01-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d02-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d03-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d04-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d05-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d06-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d07-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d08-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d09-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d10-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d11-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d12-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d13-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d14-x01-y01');
--
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d01-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d03-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d05-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d07-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d09-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d11-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d13-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d15-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d17-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d170-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d171-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d172-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d18-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d19-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d20-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d22-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d23-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d24-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d25-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d27-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d28-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d29-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d30-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d32-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d33');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d34');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d35');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d37');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d38');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d39');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d40');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d42');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d43');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d44');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d45');

INSERT INTO whitelist VALUES('CMS_2018_I1663958','d47');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d48');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d49');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d50');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d51');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d52');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d53');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d54');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d56');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d57');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d58');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d59');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d60');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d61');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d62');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d63');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d65');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d66');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d67');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d68');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d69');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d70');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d71');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d72');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d74');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d75');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d76');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d77');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d78');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d79');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d80');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d81');
-- ttbar+jets
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d96');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d98');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d100');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d102');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d104');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d106');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d108');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d110');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d112');
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d114');

-- EW W+jet
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d10');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d64');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d65');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d66');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d67');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d69');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d7');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d80');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d81');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d82');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d83');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d85');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d86');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d87');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d88');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d89');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d90');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d91');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d93');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d94');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d95');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d96');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d97');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d98');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d110');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d111');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d112');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d113');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d114');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d115');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d135');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d136');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d137');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d138');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d139');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d140');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d141');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d142');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d143');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d144');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d145');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d146');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d147');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d148');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=EL','d149');

INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d10');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d64');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d65');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d66');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d67');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d69');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d7');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d80');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d81');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d82');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d83');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d85');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d86');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d87');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d88');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d89');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d90');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d91');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d93');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d94');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d95');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d96');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d97');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d98');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d110');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d111');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d112');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d113');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d114');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d115');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d135');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d136');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d137');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d138');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d139');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d140');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d141');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d142');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d143');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d144');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d145');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d146');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d147');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d148');
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194:LMODE=MU','d149');
-- H to WW
INSERT INTO whitelist VALUES('ATLAS_2016_I1444991','d02-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1444991','d03-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1444991','d04-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1444991','d05-x01-y01');
-- ttbar
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d01');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d03');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d05');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d07');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d09');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d11');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d13');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d15');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d17');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d19');
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d21');
-- cms z+jets
INSERT INTO whitelist VALUES('CMS_2014_I1303894','d');
-- cms z+b
INSERT INTO whitelist VALUES('CMS_2013_I1256943','d');
-- ATLAS 0-lepton search
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d04-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d05-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d06-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d07-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d08-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d09-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d10-x01-y01');

-- ttbar leptonic
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d01');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d03');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d05');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d07');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d09');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d11');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d13');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d15');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d17');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d19');
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d21');
-- softdrop mass
INSERT INTO whitelist VALUES('ATLAS_2017_I1637587','d01');
INSERT INTO whitelist VALUES('ATLAS_2017_I1637587','d02');
INSERT INTO whitelist VALUES('ATLAS_2017_I1637587','d03');
-- single top
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d13');
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d15');
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d17');
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d19');
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d21');
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d23');
-- top pairs (resolved)
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d04-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d08-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d12-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d16-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d20-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d24-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d28-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d32-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d36-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d40-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d44-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d48-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d52-');
-- boosted
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d843-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d847-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d851-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d855-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d859-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d863-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d867-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d871-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d875-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d879-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d883-');
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d887-');

-- ttgamma
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d03');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d04');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d05');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d06');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d07');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d08');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d09');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d10');

-- W and Z
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=WJET','d04');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=WJET','d05');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=WJET','d06');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=ZJET','d07');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=ZJET','d08');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=ZJET','d09');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=ZJET','d10');

-- Z
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=EL','y01');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=MU','y04');

-- gamma met
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=NU','d02-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=NU','d04-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=NU','d07-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=NU','d08-x01-y01');
-- gamma ee
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=EL','d01-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=EL','d03-x01-y01');
-- gamma mumu
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=MU','d01-x01-y02');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=MU','d03-x01-y02');
-- gamma ll
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d05-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d06-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d09-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d10-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d11-x01-y01');

-- HMDY ee
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d18');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d19');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d20');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d21');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d22');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d23');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d24');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d25');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d26');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d27');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d28');

-- HMDY mumu
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d29');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d30');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d31');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d32');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d33');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d34');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d35');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d36');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d37');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d38');
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d39');

-- Hadronic top mass
INSERT INTO whitelist VALUES('CMS_2019_I1764472','d01');

-- plots with b-jet veto applied.
INSERT INTO whitelist VALUES('ATLAS_2021_I1852328','y02');

-- pick out the plots we want
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EL','d26-x01-y02');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EL','d27-x01-y02');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EL','d28-x01-y02');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EL','d29-x01-y02');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=MU','d26-x01-y01');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=MU','d27-x01-y01');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=MU','d28-x01-y01');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=MU','d29-x01-y01');


-- Measurements in a subpool will be treated as uncorrelated, so will be combined to give
-- a single likelihood, as though they were a single measurement
CREATE TABLE subpool (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    subid   TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
-- 7 TeV
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d01-x01-y01|d01-x01-y03)',0); -- inc 4l vs 2l + met
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d03|d04)',1); -- pt 4l vs 2l + met
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d05|d06)',2); -- dphi 4l vs 2l + met
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d07|d08)',3); -- mT 4l vs 2l + met

INSERT INTO subpool VALUES('ATLAS_2014_I1325553','d01-x01-y0[1-6]',0); -- r=0.4 inclusive jet y bins
INSERT INTO subpool VALUES('ATLAS_2014_I1325553','d02-x01-y0[1-6]',1); -- r=0.6 inclusive jet y bins
INSERT INTO subpool VALUES('ATLAS_2014_I1268975','d01-x01-y0[1-6]',0); -- r=0.4 dijet y* bins
INSERT INTO subpool VALUES('ATLAS_2014_I1268975','d02-x01-y0[1-6]',1); -- r=0.6 dijet y* bins
INSERT INTO subpool VALUES('ATLAS_2014_I1326641','d0[1-5]-x01-y01',0);       -- r=0.4 3 jet y* bins
INSERT INTO subpool VALUES('ATLAS_2014_I1326641','(d10|d0[6-9])-x01-y01',1); -- r=0.6 3 jet y* bins
INSERT INTO subpool VALUES('CMS_2014_I1298810','d0[1-6]-x01-y01',0);           -- r=0.5 y bins
INSERT INTO subpool VALUES('CMS_2014_I1298810','(d1[0-2]|d0[7-9])-x01-y01',1); -- r=0.7 y bins
INSERT INTO subpool VALUES('ATLAS_2014_I1307243','(d20|d1[3-9])-x01-y01',0);   -- deta jets Dy bins, inclusive
INSERT INTO subpool VALUES('ATLAS_2014_I1307243','d2[1-8]-x01-y01',1);         -- deta jets Dy bins, gap events
INSERT INTO subpool VALUES('ATLAS_2013_I1263495','d0[1-2]-x01-y01',0);         -- isolated photon eta bins
-- 8 TeV
INSERT INTO subpool VALUES('ATLAS_2016_I1457605','.',0); -- inclusive photon eta-gamma bins
INSERT INTO subpool VALUES('ATLAS_2017_I1604271','d0[1-6]-x01-y01',0);   -- inclusive jet pt, y bins, r=0.6
INSERT INTO subpool VALUES('ATLAS_2017_I1604271','(d1[0-2]|d0[7-9])',1); -- inclusive jet pt, y bins, r=0.4

INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=EL','d0[2-4]-x01-y01',0); -- low mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=EL','(d0[5-9]-x01-y01|d10-x01-y01)',1); -- medium mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=EL','d1[1-3]-x01-y01',2); -- medium mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=MU','d0[2-4]-x01-y04',3); -- low mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=MU','(d0[5-9]-x01-y04|d10-x01-y04)',4); -- low mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=MU','d1[1-3]-x01-y04',5); -- low mass phi* distributions in eta bins

INSERT INTO subpool VALUES('CMS_2016_I1454211','d02|d06',0); -- top pt (el and mu)
INSERT INTO subpool VALUES('CMS_2016_I1454211','d04|d08',0); -- top y (el and mu)


-- 13 TeV
INSERT INTO subpool VALUES('ATLAS_2018_I1634970','d0[1-6]-x01-y01',0);   -- inclusive jet pt, y bins
INSERT INTO subpool VALUES('ATLAS_2018_I1634970','(d1[0-2]|d0[7-9])',1); -- dijet mass, y* bins

INSERT INTO subpool VALUES('CMS_2016_I1459051','d0[1-7]-x01-y01','07pTvy');   -- inclusive jet pt, y bins R=0.7
INSERT INTO subpool VALUES('CMS_2016_I1459051','(d1[0-4]|d0[8-9])','04pTvy'); -- inclusive jet pt, y bins R=0.4

INSERT INTO subpool VALUES('ATLAS_2019_I1725190','d0[1-2]-x01-y01','FlavourSplit'); -- HMDY e and mu distributions

INSERT INTO subpool VALUES('CMS_2018_I1711625','d0[5-6]-x01-y01','FlavourSplit'); -- HMDY e and mu distributions

INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d01-x01-y01','M4Linclusive'); -- M4L inclusive
INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d0[2-5]-x01-y01','M4LvpT'); -- M4L vs pT
INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d0[6-9]-x01-y01','M4Lvy'); -- M4L vs y
INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d1[2-4]-x01-y01','M4LvFlavour'); -- M4L vs flavour

INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d0[2-4]-x01-y01','M4LvFlavour'); -- M4L vs flavour

INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d0[5-8]','MZ1'); -- MZ1 in different 4L regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d09|d1[0-2])','MZ2'); -- MZ1 in different 4L regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d1[3-6]','pTZ1'); -- pT(Z1) in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d1[7-9]|d20)','pTZ2'); -- pT(Z2) in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d2[1-4]','costsZ1'); -- cost(theta*) Z1 in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d2[5-8]','costsZ2'); -- cost(theta*) Z2 in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d29|d3[0-2])','Dy'); -- delta y between pairs in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d3[3-6]','Dphipairs'); -- delta phi between pairs in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d3[7-9]|d40)','Dphileptons'); -- delta phi between leading leptons in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d4[1-5]-x01-y01','ptslices'); -- ptslices
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d4[6-9]|d50)-x01-y01','yslices'); -- yslices

-- 13 TeV multijet event shapes
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d0[1-9]|d1[1-2])','TThrustMaj'); -- transverse thrust major in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d1[3-9]|d2[0-4])','ThrustMin'); -- thrust minor in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d2[5-9]|d3[0-6])','TSphericity'); --  transverse sphericity in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d3[7-9]|d4[0-8])','Aplanarity'); --  aplanarity in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d49|d5[0-9])|d60','C'); --  C in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d6[1-9]|d7[1-2])','D'); --  D in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','d7[3-5]','Multiplicity'); --  jet multiplicity in non-overlapping regions.

-- 13TeV HMDY search
INSERT INTO subpool VALUES('ATLAS_2019_I1725190','d0[1-2]','Mass'); --  electrons and muons

CREATE TABLE normalization (
--  analysis id, plot pattern, norm factor for ref data, number of x units an n_event distribution is differential in (nx; 0 if not applicable).
--
--  The normalisation is applied on the assumption the Rivet plots have been area-normalised to one, i.e. are
--  presented as 1/sigma(fid) * dsigma(fid)/dX where X is some kinematic variable.
--
--  Therefore the norm factor number needs to be the integrated cross section for the fiducial region considered,
--  and should be in pb since that is what Rivet reports.
--
--  The nx applies for n_event distributions in searches which typically have no uncertainty in y. If the plot
--  is in e.g. n_events/10 GeV, to get the number of events, we multiply by the bin width and divide by nx; from this
--  the Poisson (~ root(n)) uncertainty can be calculated. nx < 0 means the bin width is constant and the plot is just differential in that. (nx = 0 means this is already a differential cross section with uncertinties.)

    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    norm    REAL NOT NULL,
    nxdiff INT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
-- CMS 3L is normalised in the Rivet routine to 24.09 pb which is allegedly the WZ cross-section
-- in the region.
-- Note that way the signal is dealt within Contur means this is turned into a cross-section
-- normalisation just as though the scaling were to unity; the 24.09 makes rather than 1.0 makes
-- no difference. However, the data are presented as WZ cross sections, that is is (a) they are
-- not nu lll cross sections but (b) and they not area normalised. What this means is we have to
-- turn them into nu lll cross sections to compare to the MC. This means multiplying by the
-- BR WZ --> lll nu where lll are electrons or muons.
-- This is still a fudge, since we don't know the correction for the fiducial cuts, but that
-- should at least lead to an underestimate of any sensitivity.
INSERT INTO normalization VALUES('CMS_2016_I1487288','d',0.0363*2.0*0.1080*2.0,0); -- 3l

-- 7 TeV 4L (cross section and BF to leptons)
INSERT INTO normalization VALUES('ATLAS_2012_I1203852:LMODE=LL','(d03|d05|d07)',0.0254,0); -- 4l
INSERT INTO normalization VALUES('ATLAS_2012_I1203852:LMODE=LNU','(d04|d06|d08)',0.0127,0); -- 2l met

-- Normalisation from ATLAS aux material
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d0[1-6]' ,48200000.0/33000.0,0); -- dijet selection
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d0[7-9]',14400.0/33000.0,0); -- top
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d1[0-4]',14400.0/33000.0,0); -- top
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d1[5-9]',13900.0/33000.0,0); -- W selection
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d2[0-2]',13900.0/33000.0,0); -- W selection
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d2[3-8]',48200000.0/33000.0,0); -- dijet selection
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d29',14400.0/33000.0,0); -- top
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d3[0-6]',14400.0/33000.0,0); -- top
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d3[7-9]',13900.0/33000.0,0); -- W selection
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','d4[0-4]',13900.0/33000.0,0); -- W selection

-- normalisation for 8TeV 3Jet mode using sum of eventcount
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d01-x01-y01',7.8344933,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d02-x01-y01',7.7247165,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d03-x01-y01',10.0000004,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d04-x01-y01',10.0000007,0);

--normalisation for 13TeV 3Jet mode using sum of eventcount
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d05-x01-y01',7.6331767,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d06-x01-y01',7.5335873,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d07-x01-y01',10.0000004,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d08-x01-y01',10.0000005,0);
-- more attention needed if using the ZJet mode results other than these two modes.
-- normalisation factor with integreated cross section in pb for CMS_2020_I1814328
INSERT INTO normalization VALUES('CMS_2020_I1814328','d02-x01-y01',122.0,0);
INSERT INTO normalization VALUES('CMS_2020_I1814328','d04-x01-y01',122.0,0);
INSERT INTO normalization VALUES('CMS_2020_I1814328','d05-x01-y01',122.0,0);
INSERT INTO normalization VALUES('CMS_2020_I1814328','d06-x01-y01',122.0,0);
INSERT INTO normalization VALUES('CMS_2020_I1814328','d07-x01-y01',122.0,0);

-- normalisation factor with integrated cross section in pb for ATLAS_2019_I1768911 

INSERT INTO normalization VALUES('ATLAS_2019_I1768911','d27-x01-y01',736.2,0); -- NB these are approx (LO born) but ok
INSERT INTO normalization VALUES('ATLAS_2019_I1768911','d28-x01-y01',736.2,0);

-- this is BR to a single charged lepton, needed when the xsec is report as a W
-- and the generator reports the final state.
-- INSERT INTO normalization VALUES('ATLAS_2014_I1319490_MU','d',0.108059,0);
-- INSERT INTO normalization VALUES('ATLAS_2014_I1319490_EL','d',0.108059,0);
-- INSERT INTO normalization VALUES('CMS_2014_I1303894','d',0.108059,0);

-- these are the integrated cross section of the plot, in pb
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d01',5.88,0);
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d02',1.82,0);
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d03',1.10,0);
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d04',0.447,0);
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d05',0.066,0);
-- these are the integrated cross section of the plot, in pb
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d23',1.45,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d24',1.03,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d25',0.97,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d02',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d03',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d04',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d14',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d26',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d05',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d06',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d07',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d08',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d09',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d10',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d15',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d17',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d18',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d19',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d20',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d21',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d22',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d27',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d11',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d12',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d13',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d16',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d28',5.59,0);
-- these are the integrated cross section of the plot, in pb
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d23',1.45,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d24',1.03,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d25',0.97,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d02',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d03',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d04',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d14',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d26',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d05',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d06',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d07',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d08',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d09',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d10',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d15',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d17',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d18',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d19',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d20',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d21',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d22',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d27',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d11',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d12',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d13',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d16',5.59,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d28',5.59,0);

-- CMS single jet mass stuff here
-- WJETS. Cross section in pb
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d52',1.06,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d56',1.06,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d60',1.06,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d64',1.06,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d68',1.06,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d53',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d57',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d61',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d65',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d69',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d72',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d54',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d58',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d62',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d66',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d70',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d73',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d55',0.43,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d59',0.43,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d63',0.43,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d67',0.43,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d71',0.43,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','d74',0.43,0);
-- ZJETS. Cross section in pb
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d29',0.852,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d33',0.852,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d37',0.852,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d41',0.852,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d45',0.852,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d30',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d34',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d38',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d42',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d46',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d49',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d31',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d35',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d39',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d43',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d47',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d50',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d32',0.141,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d36',0.141,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d40',0.141,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d44',0.141,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d48',0.141,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','d51',0.141,0);
-- 7 TeV WW cross section in fb
INSERT INTO normalization VALUES('ATLAS_2013_I1190187','d04-x01-y01',392.6,0);
-- 8 TeV b hadron cross section in fb
INSERT INTO normalization VALUES('ATLAS_2017_I1598613:BMODE=3MU','d',17700000,0);
-- 7 TeV LHCb stuff
INSERT INTO normalization VALUES('LHCB_2012_I1208102','d',76,0);
-- 20 GeV threshold
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d04-x01-y01',6.3,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d05-x01-y01',6.3,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d06-x01-y01',6.3,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d07-x01-y01',6.3,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d08-x01-y01',6.3,0);
-- 10 GeV threshold
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d03',16.0,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d04-x01-y02',16.0,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d05-x01-y02',16.0,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d06-x01-y02',16.0,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d07-x01-y02',16.0,0);
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d08-x01-y02',16.0,0);

-- ttbb in fb
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d05-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d07-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d09-x01-y01',2450,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d11-x01-y01',2450,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d13-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d15-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d17-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d19-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d21-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d23-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d25-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d27-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d29-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d31-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d33-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d35-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d37-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d39-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d41-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d43-x01-y01',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d45-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d47-x01-y01',359,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','d49-x01-y01',359,0);
-- HMDY 13 TeV search
INSERT INTO normalization VALUES('ATLAS_2019_I1725190','d01-x01-y01',0,10);
INSERT INTO normalization VALUES('ATLAS_2019_I1725190','d02-x01-y01',0,10);
-- 13TeV SUSY MET 0-lepton search
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d04-x01-y01',0,-1);
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d05-x01-y01',0,-1);
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d06-x01-y01',0,-1);
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d07-x01-y01',0,-1);
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d08-x01-y01',0,-1);
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d09-x01-y01',0,-1);
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','d10-x01-y01',0,-1);
-- ATLAS softdrop mass
INSERT INTO normalization VALUES('ATLAS_2017_I1637587','d01-x01-y01',140,0);
INSERT INTO normalization VALUES('ATLAS_2017_I1637587','d02-x01-y01',190,0);
INSERT INTO normalization VALUES('ATLAS_2017_I1637587','d03-x01-y01',210,0);
-- ttbar gamma
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d03',521,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d04',521,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d05',521,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d06',69,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d07',69,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d08',69,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d09',69,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d10',69,0);

-- 13 TeV multijet event shapes. cross sections in pb
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d01|d13|d25|d37|d49|d61)',371.7,0);  -- 3jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d02|d14|d26|d38|d50|d62)',371.7,0);  -- 4jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d03|d15|d27|d39|d51|d63)',371.7,0);  -- 5jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d04|d16|d28|d40|d52|d64)',371.7,0);  -- 6jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d05|d17|d29|d41|d53|d65)',35.5,0);  -- 3jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d06|d18|d30|d42|d54|d66)',35.5,0);  -- 4jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d07|d19|d31|d43|d55|d67)',35.5,0); -- 5jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d08|d20|d32|d44|d56|d68)',35.5,0); -- 6jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d09|d21|d33|d45|d57|d69)',7.09,0);   -- 3jets, high HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d10|d22|d34|d46|d58|d70)',7.09,0); -- 4jets, high HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d11|d23|d35|d47|d59|d71)',7.09,0); -- 5jets, high HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d12|d24|d36|d48|d60|d72)',7.09,0); -- 6jets, high HT

-- 8 TeV W, Z pT
INSERT INTO normalization VALUES('CMS_2016_I1471281:VMODE=Z','d09',440,0);
INSERT INTO normalization VALUES('CMS_2016_I1471281:VMODE=W','d08',6290,0);

--Track-based 13 TeV in ATLAS - pb
INSERT INTO normalization VALUES('ATLAS_2016_I1467230','d',61589403974,0);
INSERT INTO normalization VALUES('ATLAS_2016_I1419652','d',52176470588,0);
INSERT INTO normalization VALUES('ATLAS_2020_I1790256','d',14750000/139000,0); 





-- This is a table to store any histograms which can only be used
-- if running in SM theory mode
CREATE TABLE metratio (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO metratio VALUES('ATLAS_2017_I1609448','d');


-- This is a table to store histograms which use tracks only
-- (Useful for e.g. Dark Shower models where we may not trust calorimeter jet calibration
CREATE TABLE tracksonly (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO tracksonly VALUES('ATLAS_2016_I1419652','d');
INSERT INTO tracksonly VALUES('ATLAS_2016_I1467230','d');
INSERT INTO tracksonly VALUES('ATLAS_2019_I1740909','d');
INSERT INTO tracksonly VALUES('ATLAS_2020_I1790256','d');

-- This is a table to store histograms which are very sensitive to soft physics
-- and so should not be used by default
CREATE TABLE softphysics (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO softphysics VALUES('ATLAS_2016_I1419652','d');
INSERT INTO softphysics VALUES('ATLAS_2016_I1467230','d');
INSERT INTO softphysics VALUES('ATLAS_2019_I1740909','d');
INSERT INTO softphysics VALUES('ATLAS_2020_I1790256','d');
INSERT INTO softphysics VALUES('CMS_2021_I1932460','d');


-- This is a table to store any histograms which require and use SM theory whatever run mode is used.
-- This includes searches, which require a background model, ratios to SM, and single-point histograms
CREATE TABLE needtheory (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO needtheory VALUES('ATLAS_2017_I1609448','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1458270','d');
INSERT INTO needtheory VALUES('ATLAS_2019_I1725190','d');
INSERT INTO needtheory VALUES('ATLAS_2021_I1887997','yy_xs');
INSERT INTO needtheory VALUES('ATLAS_2021_I1852328','d01-x01-y02');
INSERT INTO needtheory VALUES('ATLAS_2019_I1738841','d');
INSERT INTO needtheory VALUES('ATLAS_2012_I1203852:LMODE=LL','d');
INSERT INTO needtheory VALUES('ATLAS_2012_I1203852:LMODE=LNU','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1492320:LMODE=3L','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1492320:LMODE=2L2J','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1448301:LMODE=EL','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1448301:LMODE=NU','d02');
INSERT INTO needtheory VALUES('ATLAS_2016_I1448301:LMODE=NU','d04');
INSERT INTO needtheory VALUES('CMS_2019_I1753720','d');
INSERT INTO needtheory VALUES('LHCB_2018_I1662483','d');


-- This is a table to store any histograms which are made using
-- background-subtracted Higgs gamma-gamma signal and which
-- should therefore not be used to exclude continuum diphotons
CREATE TABLE higgsgg (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO higgsgg VALUES('ATLAS_2014_I1306615','d');

-- This is a table to flag search distributions (ie event count histograms which are not unfolded)
CREATE TABLE searches (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO searches VALUES('ATLAS_2016_I1458270','d');
INSERT INTO searches VALUES('ATLAS_2019_I1725190','d');

-- This is a table to store any histograms which are made using
-- background-subtracted Higgs ww signal and which
-- should therefore not be used to exclude bsm top/w production
CREATE TABLE higgsww (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO higgsww VALUES('CMS_2017_I1467451','d');
INSERT INTO higgsww VALUES('ATLAS_2016_I1444991','d');

-- This is a table to store ATLAS WZ measurements which assume the SM in their neutrino flavour assignment.
CREATE TABLE atlaswz (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO atlaswz VALUES('ATLAS_2016_I1469071','d');

-- This is a table to store measurements which have a secret b-jet veto
CREATE TABLE bveto (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO bveto VALUES('CMS_2014_I1303894','d');
INSERT INTO bveto VALUES('CMS_2016_I1491953','d');
INSERT INTO bveto VALUES('CMS_2017_I1610623','d');
INSERT INTO bveto VALUES('CMS_2017_I1467451','d');
INSERT INTO bveto VALUES('CMS_2020_I1794169','d');
-- INSERT INTO bveto VALUES('CMS_2020_I1837084','d');

--

-- Index the theory predictions that Contur knows about.
--------------------------------------------------------
-- id: the full analysis name, including any options
-- inspids: inspire IDs of theory references
-- origin: where the data comes from. See contur/run/run_mkthy.py for meaning
-- pattern: histogram patterns these predictions are for
-- axis: for HEPData record, the name of the axis to take the theory from
-- file_name: the name of the file the prediction is stored in. The files contur uses by default end in -Theory.yoda
-- short_description: for plot legends 
-- long_description: for web pages, does not need to repeat the short description
CREATE TABLE theory_predictions (
    id      TEXT NOT NULL,
    inspids    TEXT,
    origin     TEXT,
    pattern    TEXT,
    axis       TEXT,
    file_name TEXT,
    short_description TEXT,
    long_description TEXT,
    FOREIGN KEY(id) REFERENCES analysis(id)
    UNIQUE(file_name, pattern, id)
);
INSERT INTO theory_predictions VALUES('ATLAS_2019_I1772071','1736301,562391,946998,760143','REF','y01','y02',
       'ATLAS_2019_I1772071-Theory.yoda',
       'Sherpa NLO',
       'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('CMS_2021_I1932460','1932460','HEPDATA','d50-x01-y01',NULL,
       'CMS_2021_I1932460-Theory.yoda',
       'Powheg NLO 2-> 2 + Double-parton scattering',
       'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('CMS_2019_I1753720','1753720','HEPDATA','d01-x01-y01',NULL,
       'CMS_2019_I1753720-Theory.yoda',
       'MadGraph+Pythia8',
       'From measurement paper in Figure 3');
INSERT INTO theory_predictions VALUES('ATLAS_2019_I1738841','1738841','HEPDATA','d01-x01-y01',NULL,
       'ATLAS_2019_I1738841-Theory.yoda',
       'Powheg+Pythia8',
       'From measurement paper in page 8 above the diagram.');
       
INSERT INTO theory_predictions VALUES('ATLAS_2021_I1887997','1887997','HEPDATA','ph1|ph2|yy_cosTS|yy_m|yy_xs','_NNLO',
       'ATLAS_2021_I1887997-Theory.yoda',
       'NNLOJet doi.org/10.17182/hepdata.104925',
       'Taken from the HEPData record of the experimental paper');
-- diphoton mass not so well described. Another good prediction here: https://inspirehep.net/literature/2072920 which looks like it might
-- describe that better

INSERT INTO theory_predictions VALUES('ATLAS_2021_I1887997','1887997','HEPDATA','yy_pT|yy_phiStar|yy_piMDphi','_SHERPA',
       'ATLAS_2021_I1887997-Theory.yoda',
       'Sherpa doi.org/10.17182/hepdata.104925',
       'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('ATLAS_2012_I1199269','1653472','SPECIAL','',NULL,
       'ATLAS_2012_I1199269-Theory.yoda',
       'Catani et al',
       'NNLO QCD, read from figures in paper.');
INSERT INTO theory_predictions VALUES('ATLAS_2012_I1203852:LMODE=LL','845712,920312,789541','RAW','d01-x01-y01|d01-x01-y02',NULL,
       'ATLAS_2012_I1203852:LMODE=LL-Theory.yoda',
       'PowhegBox+gg2zz',
       'From measurement paper. See additional references therein.');
INSERT INTO theory_predictions VALUES('ATLAS_2012_I1203852:LMODE=LNU','845712,920312,789541','RAW','d01-x01-y03',NULL,
       'ATLAS_2012_I1203852:LMODE=LNU-Theory.yoda',
       'PowhegBox+gg2zz',
       'From measurement paper. See additional references therein.');
-- INSERT INTO theory_predictions VALUES('ATLAS_2013_I1230812:LMODE=EL','NK','RAW','d',NULL,
--       'ATLAS_2013_I1230812-Theory.yoda',
--      'Not known',
--      'Think this came from Herwig/Matchbox, needs to be checked/replaced.');
-- INSERT INTO theory_predictions VALUES('ATLAS_2013_I1230812:LMODE=MU','NK','RAW','d',NULL,
--      'ATLAS_2013_I1230812-Theory.yoda',
--      'Not known',
--      'Think this came from Herwig/Matchbox, needs to be checked/replaced.');
INSERT INTO theory_predictions VALUES('ATLAS_2014_I1306615','1095242,1239172','RAW','d',NULL,
       'ATLAS_2014_I1306615-Theory.yoda',
       'HRES 2.2',
       'Read from plot(s) in the measurement paper, since only the non-gg theory is provided in HEPData. \n See measurement paper for more details of the calculation.');
INSERT INTO theory_predictions VALUES('ATLAS_2014_I1310835','1118569,1310835','REF','y01','y02',
       'ATLAS_2014_I1310835-Theory.yoda',
       'Powheg Minlo HJ + non-ggF',
       'See paper for more details. HEPData record at https://doi.org/10.17182/hepdata.78567.v1  ');
INSERT INTO theory_predictions VALUES('ATLAS_2014_I1310835','1095242,1239172,1310835','REF','y01','y03',
       'ATLAS_2014_I1310835-Theory-HRES.yoda',
       'HRES + non-ggF',
       'See paper for more details. HEPData record at https://doi.org/10.17182/hepdata.78567.v1  ');
INSERT INTO theory_predictions VALUES('ATLAS_2015_I1397637','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2015_I1397637-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2015_I1404878','1838799,1838807','RAW','d',NULL,
       'ATLAS_2015_I1404878-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2015_I1408516:LMODE=MU','1673183','SPECIAL','d',NULL,
       'ATLAS_2015_I1408516:LMODE=MU-Theory.yoda',
       'Bizon et al',
       'Digitised files from author. NNLO + N3LL: NNLOJET + RADISH.');
INSERT INTO theory_predictions VALUES('ATLAS_2015_I1408516:LMODE=EL','1673183','SPECIAL','d',NULL,
       'ATLAS_2015_I1408516:LMODE=EL-Theory.yoda',
       'Bizon et al',
       'Digitised files from author. NNLO + N3LL: NNLOJET + RADISH.');       
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1448301:LMODE=NU','897881','RAW','d02-x01-y01|d04-x01-y01',NULL,
       'ATLAS_2016_I1448301:LMODE=NU-Theory.yoda',
       'MCFM',
       'MCFM NLO calculations, from measurement paper');       
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1448301:LMODE=EL','1357993,897881','RAW','d01-x01-y01|d03-x01-y01',NULL,
       'ATLAS_2016_I1448301:LMODE=EL-Theory.yoda',
       'GKR and MCFM',
       'MCFM NLO and (for Z-gamma only) Grazzini, Kalleit, Rathlev NNLO Calculations, from measurement paper');
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1448301:LMODE=MU','1357993,897881','RAW','d01-x01-y02|d03-x01-y02',NULL,
       'ATLAS_2016_I1448301:LMODE=MU-Theory.yoda',
       'GKR and MCFM',
       'MCFM NLO and (for Z-gamma only) Grazzini, Kalleit, Rathlev NNLO Calculations, from measurement paper');       
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1457605','1727794','SPECIAL','d',NULL,
       'ATLAS_2016_I1457605-Theory.yoda',
       'NNLO QCD Chen et al',
       'NLO QCD, Xuan Chen, Thomas Gehrmann, Nigel Glover, Marius Hoefer, Alexander Huss');
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1458270','1458270','REF','d','y02',
       'ATLAS_2016_I1458270-Theory.yoda',
       'Expected SM events',
       'Background expectation from search paper.');
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1467454:LMODE=MU','1182519,725573,877524','SPECIAL','d',NULL,
       'ATLAS_2016_I1467454:LMODE=MU-Theory.yoda',
       'FEWZ',
       'Predictions from the paper, taken from the ll ratio plot (Born) but applied to the dressed 
       level ee & mm data as mult. factors.');
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1467454:LMODE=EL','1182519,725573,877524','SPECIAL','d',NULL,
       'ATLAS_2016_I1467454:LMODE=EL-Theory.yoda',
       'FEWZ',
       'Predictions from the paper, taken from the ll ratio plot (Born) but applied to the dressed 
       level ee & mm data as mult. factors.');
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1492320:LMODE=3L','1293923','RAW','d01-x01-y01',NULL,
       'ATLAS_2016_I1492320:LMODE=3L-Theory.yoda',
       'MadGraph',
       'Taken from measurement paper');
INSERT INTO theory_predictions VALUES('ATLAS_2016_I1492320:LMODE=2L2J','1293923','RAW','d01-x01-y02',NULL,
       'ATLAS_2016_I1492320:LMODE=2L2J-Theory.yoda',
       'MadGraph',
       'Taken from measurement paper');

INSERT INTO theory_predictions VALUES('ATLAS_2017_I1591327','1664354,939520','SPECIAL','d',NULL,
       'ATLAS_2017_I1591327-Theory.yoda',
       'NNLO QCD',
       'Bouzid Boussaha, Farida Iddir, Lahouari Semlala; 2gamma from Catani, Cieri, de Florian, Ferrera and Grazzini, Diphoton production at hadron colliders: a fully-differential QCD calculation at NNLO.');
-- Note the ptGG is very poorly described, but better here, for example: https://inspirehep.net/literature/1893572

INSERT INTO theory_predictions VALUES('ATLAS_2017_I1609448','1736301,1609448','REF','d','y02',
       'ATLAS_2017_I1609448-Theory.yoda',
       'SM (Sherpa $\times$ NNLO)',
       'From Measurement paper.');
INSERT INTO theory_predictions VALUES('ATLAS_2017_I1614149','1838799,1980698','RAW','d',NULL,
       'ATLAS_2017_I1614149-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2017_I1645627','1727794','SPECIAL','d',NULL,
       'ATLAS_2017_I1645627-Theory.yoda',
       'NNLO QCD arXiv:1904.01044',
       'Isolated photon and photon+jet production at NNLO QCD accuracy, from Chen et al');
INSERT INTO theory_predictions VALUES('ATLAS_2018_I1646686','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2018_I1646686-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2018_I1656578','1838799,1838807','RAW','d',NULL,
       'ATLAS_2018_I1656578-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2019_I1720442','1736301,1720442','REF','d','y02',
       'ATLAS_2019_I1720442-Theory.yoda',
       'Sherpa+NLO EW',
       'See measurement paper for full details. HEPData record at https://doi.org/10.17182/hepdata.84818');
INSERT INTO theory_predictions VALUES('ATLAS_2019_I1725190','1725190','SPECIAL','d',NULL,
       'ATLAS_2019_I1725190-Theory.yoda',
       'Background fit',
       'The \"Theory prediction\" is the background fit to data from the measurement paper.');
INSERT INTO theory_predictions VALUES('ATLAS_2019_I1750330:TYPE=BOTH','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2019_I1750330:TYPE=BOTH-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2019_I1759875','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2019_I1759875-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2021_I1849535','1736301,1849535','REF','y01','y02',
       'ATLAS_2021_I1849535-Theory.yoda',
       'Sherpa+NLO EW',
       'See measurement paper for full details. HEPData record at https://doi.org/10.17182/hepdata.94413.v1');
INSERT INTO theory_predictions VALUES('ATLAS_2021_I1852328','1736301,1852328','SPECIAL','d',NULL,
       'ATLAS_2021_I1852328-Theory.yoda',
       'MATRIX nNNLO x NLO EW',
       'Rescaled to b-veto measurement using data. See measurement paper for full details. HEPData record at https://doi.org/10.17182/hepdata.100511.v1');

INSERT INTO theory_predictions VALUES('CMS_2016_I1491950','1838799,1980698','RAW','d',NULL,
       'CMS_2016_I1491950-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('CMS_2017_I1467451','1095242,1239172','SPECIAL','d',NULL,
       'CMS_2017_I1467451-Theory.yoda',
       'HRes 2.2',
       'Calculation from measurement paper. See that paper for more details.');
INSERT INTO theory_predictions VALUES('CMS_2017_I1518399','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2017_I1518399-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('CMS_2018_I1662081','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2018_I1662081-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('CMS_2018_I1663958','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2018_I1663958-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('CMS_2019_I1764472','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2019_I1764472-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('LHCB_2018_I1662483','1838799,1838807,1980698','RAW','d',NULL,
       'LHCB_2018_I1662483-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('ATLAS_2018_I1634970','1838799','RAW','d',NULL,
       'ATLAS_2018_I1634970-Theory.yoda',
       'Powheg',
       'As used in Altakach et all arXiv:2111.15406');

COMMIT;
