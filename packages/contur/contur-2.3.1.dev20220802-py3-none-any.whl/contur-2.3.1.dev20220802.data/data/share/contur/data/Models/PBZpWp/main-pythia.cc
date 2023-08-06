#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC2.h"
#include "Pythia8Plugins/PowhegHooks.h"
using namespace Pythia8;

int main(int argc, char* argv[]) {

  // Check that correct number of command-line arguments
  if (argc != 4) {
    cerr << " Unexpected number of command-line arguments. \n You are"
         << " expected to provide one input and one output file name. \n"
         << " Program stopped! " << endl;
    return 1;
  }
  
  // Confirm that external files will be used for input and output.
  cout << "\n >>> The lh events will be read from file " << argv[2]
       << " <<<\n >>> The Number of events is " << argv[3]
       << " <<< \n >>> HepMC events will be written to file "
       << argv[1] << " <<< \n" << endl;

  // Interface for conversion from Pythia8::Event to HepMC event.
  HepMC::Pythia8ToHepMC ToHepMC;

  // Specify file where HepMC events will be stored.
  HepMC::IO_GenEvent ascii_io(argv[1], std::ios::out);

  // Generator.
  Pythia pythia;

  // lhe input file, events will be read from the .lhe file
  pythia.readString("Beams:frameType = 4"); // Choice of frame for the two colliding particles. For options 4 the beam identities are obtained by the Les Houches information. 
  pythia.readString("Beams:LHEF ="+std::string(argv[2]));
  // allow top and anti-top decay
  pythia.readString("6:mayDecay = on"); 
  pythia.readString("-6:mayDecay = on");
  pythia.readString("6:m0 = 172.5"); // top mass
  // pythia.readString("6:mWidth = "); // top width
  //pythia.readString("6:doForceWidth = on");
  pythia.readString("23:m0 = 91.1876"); // Z mass
  pythia.readString("23:mWidth = 2.4952"); // Z width
  pythia.readString("23:doForceWidth = on");
  pythia.readString("24:m0 = 80.385"); // W mass
  pythia.readString("24:mWidth = 2.085"); // W width
  pythia.readString("24:doForceWidth = on");
  // allow only leptonic decays of W
  // pythia.readString("24:0:onMode = off");
  // pythia.readString("24:1:onMode = off");
  // pythia.readString("24:2:onMode = off");
  // pythia.readString("24:3:onMode = off");
  // pythia.readString("24:4:onMode = off");
  // pythia.readString("24:5:onMode = off");
  // pythia.readString("24:8:onMode = off");
  // alphaEM
  pythia.readString("SigmaProcess:alphaEMorder = -1"); // fixed value of alEM at the MZ
  pythia.readString("StandardModel:alphaEMmZ = 0.00788084168"); // it's value at the MZ
  // Weinberg angle 1 - MW**2/MZ**2
  //pythia.readString("StandardModel:sin2thetaW = 0.228686755");
  //pythia.readString("StandardModel:sin2thetaWbar = 0.228686755");
  pythia.readString("StandardModel:sin2thetaW = 0.23116");
  pythia.readString("StandardModel:sin2thetaWbar = 0.23116");
  // we leave the Z boson couplings unchanged, pythia manual mentions that
  // they are calculated from the sin2thetaWbar value, in which case 
  // they should be correct, albeit inconsistent, if the user sets them to
  // outrageous values

  // switch off QED radiation
  pythia.readString("SpaceShower:QEDshowerByQ = on"); // From quarks
  pythia.readString("SpaceShower:QEDshowerByL = on"); // From Leptons
  pythia.readString("TimeShower:QEDshowerByQ = on"); // From quarks
  pythia.readString("TimeShower:QEDshowerByL = on"); // From Leptons
  cout << "pythia_init: QEDshower on" << endl;

  // SpaceShower(TimeShower):pTmaxMatch -- pT veto setting for ISR(FSR)
  // 0 ... the default Pythia setting
  // 1 ... Pythia will use scalup to limit radiation
  // 2 ... Pythia will use a UserHook to veto
  // PowhegHook related settings
  PowhegHooks *powhegHooks = NULL;
  int veto = 1; // see PowhegHook settings above
  int vetoCount = 3; // see above
  int pThard = 0; // see above
  int pTdef = 1; // see above
  int pTemt = 0; // see above
  int emitted = 0; // see above
  int nFinal = 2; // number of final state particles at Born level
 
  // use UserHooks for ISR and FSR
  pythia.readString("SpaceShower:pTmaxMatch = 2");
  pythia.readString("TimeShower:pTmaxMatch = 2");
  // set up user hooks
  pythia.readString("POWHEG:nFinal = " + std::to_string(nFinal));
  pythia.readString("POWHEG:veto = " + std::to_string(veto));
  pythia.readString("POWHEG:vetoCount = " + std::to_string(vetoCount));
  pythia.readString("POWHEG:pThard = " + std::to_string(pThard));
  pythia.readString("POWHEG:pTemt = " + std::to_string(pTemt));
  pythia.readString("POWHEG:emitted = " + std::to_string(emitted));
  pythia.readString("POWHEG:pTdef = " + std::to_string(pTdef));
  powhegHooks = new PowhegHooks();
  pythia.setUserHooksPtr((UserHooks *) powhegHooks);

  // switch on matrix element corrections (this is the default I believe)
  pythia.readString("TimeShower:MEcorrections = on");
  pythia.readString("SpaceShower:MEcorrections = on");                                                                                                                                                          
  // underlying event
  pythia.readString("Tune:preferLHAPDF=0"); // using pythia built-in PDF
  pythia.readString("Tune:pp=14"); // Monash 2013 tune

  // switch off multiparton interaction
  pythia.readString("PartonLevel:MPI = on");
  // switch off hadronization
  pythia.readString("HadronLevel:all = on");
 
  // show x event records
  pythia.readString("Next:numberShowEvent = 1");

  // Extract settings to be used in the main program.
  int    nEvent    = atoi(argv[3]);
  int    nAbort    = 3;

  // Initialization.
  pythia.init();

  // Begin event loop.
  int iAbort = 0;
  for (int iEvent = 0; iEvent < nEvent; ++iEvent) {

    // Generate event.
    if (!pythia.next()) {

      // If failure because reached end of file then exit event loop.
      if (pythia.info.atEndOfFile()) {
        cout << " Aborted since reached end of Les Houches Event File\n";
        break;
      }

      // First few failures write off as "acceptable" errors, then quit.
      if (++iAbort < nAbort) continue;
        cout << " Event generation aborted prematurely, owing to error!\n";
        break;
      }

    // Construct new empty HepMC event and fill it.
    // Units will be as chosen for HepMC build, but can be changed
    // by arguments, e.g. GenEvt( HepMC::Units::GEV, HepMC::Units::MM)
    HepMC::GenEvent* hepmcevt = new HepMC::GenEvent();
    ToHepMC.fill_next_event( pythia, hepmcevt );

    // Write the HepMC event to file. Done with it.
    ascii_io << hepmcevt;
    delete hepmcevt;

  // End of event loop. Statistics.
  }
  pythia.stat();

  // Done.
  return 0;
}

