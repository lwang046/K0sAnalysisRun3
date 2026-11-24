/*
 Dimuon HLT bits for DY reference selection.

 Ported (lean subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/interface/TriggerAnalyzer.h
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Run3 / K0sAnalysisRun3 adaptations:
   - Owner: DisplacedV0Ntuple* (was multilep*)
   - Configurable HLT OR list via PSet "hltPaths" (baseline Mass3p8)
   - Dropped year-by-year HNL trigger cocktail, MET filters, Ele32 emulation,
     and trigger-object matching (not needed for DY+V0)
*/
#ifndef DisplacedV0_TriggerAnalyzer_h
#define DisplacedV0_TriggerAnalyzer_h

#include <map>
#include <string>
#include <vector>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "TTree.h"

class DisplacedV0Ntuple;

class TriggerAnalyzer {
private:
  std::vector<std::string> triggersToSave_;
  std::map<std::string, bool> flag_;
  std::map<std::string, int> index_;
  bool passDimuonHLT_{false};
  bool reIndex_{true};
  unsigned int lastRun_{0};
  DisplacedV0Ntuple* ntuple_{nullptr};

  void indexFlags(const edm::Event& iEvent, const edm::TriggerResults& results);

public:
  TriggerAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple);
  ~TriggerAnalyzer() = default;

  void beginJob(TTree* outputTree);
  void analyze(const edm::Event& iEvent);
};

#endif
