/*
 Dimuon HLT bits for DY reference selection.

 Ported (lean subset) from LukaLambrecht/K0sAnalysis
   ntuplizer/heavyNeutrino/multilep/src/TriggerAnalyzer.cc
   commit 2a132385aec7e15d1bbdfb038edf0534bb4855b8 (2024-08-20)

 Keeps upstream TriggerResults indexing / accept logic; HLT list is config-driven
 for Run3 Mass3p8 (+ optional OR companions).
*/

#include "K0sAnalysis/DisplacedV0/interface/TriggerAnalyzer.h"
#include "K0sAnalysis/DisplacedV0/plugins/DisplacedV0Ntuple.h"

#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"

#include <iostream>

TriggerAnalyzer::TriggerAnalyzer(const edm::ParameterSet& iConfig, DisplacedV0Ntuple* ntuple)
    : ntuple_(ntuple) {
  if (iConfig.existsAs<std::vector<std::string>>("hltPaths")) {
    triggersToSave_ = iConfig.getParameter<std::vector<std::string>>("hltPaths");
  } else {
    triggersToSave_ = {"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8"};
  }
}

void TriggerAnalyzer::beginJob(TTree* outputTree) {
  reIndex_ = true;
  for (const auto& name : triggersToSave_) {
    flag_[name] = false;
    index_[name] = -1;
    outputTree->Branch(name.c_str(), &flag_[name], (name + "/O").c_str());
  }
  // Logical OR of configured dimuon paths (AN Tab. 4 cocktail analogue)
  outputTree->Branch("passDimuonHLT", &passDimuonHLT_, "passDimuonHLT/O");
}

void TriggerAnalyzer::indexFlags(const edm::Event& iEvent, const edm::TriggerResults& results) {
  for (const auto& t : triggersToSave_) {
    index_[t] = -1;
  }

  const edm::TriggerNames& triggerNames = iEvent.triggerNames(results);
  std::cout << "[TriggerAnalyzer] Available HLT paths (matching configured list):" << std::endl;
  for (unsigned i = 0; i < results.size(); ++i) {
    const std::string& fullName = triggerNames.triggerName(i);
    for (const auto& t : triggersToSave_) {
      // Upstream matches "HLT_..._v" prefix against menu versions
      const std::string prefix = t + "_v";
      if (fullName.find(prefix) == 0 || fullName == t) {
        index_[t] = static_cast<int>(i);
        std::cout << "  " << fullName << "  --> saving as " << t << std::endl;
      }
    }
  }
  for (const auto& t : triggersToSave_) {
    if (index_[t] < 0) {
      std::cout << "[TriggerAnalyzer] WARNING: " << t
                << " not found in TriggerResults — bit will be false" << std::endl;
    }
  }
}

void TriggerAnalyzer::analyze(const edm::Event& iEvent) {
  for (auto& kv : flag_) kv.second = false;
  passDimuonHLT_ = false;

  edm::Handle<edm::TriggerResults> triggerResults;
  iEvent.getByToken(ntuple_->triggerToken, triggerResults);
  if (!triggerResults.isValid()) return;

  if (reIndex_ || iEvent.id().run() != lastRun_) {
    indexFlags(iEvent, *triggerResults);
    reIndex_ = false;
    lastRun_ = iEvent.id().run();
  }

  for (const auto& t : triggersToSave_) {
    const int idx = index_[t];
    if (idx < 0) {
      flag_[t] = false;
    } else {
      flag_[t] = triggerResults->accept(static_cast<unsigned>(idx));
    }
    if (flag_[t]) passDimuonHLT_ = true;
  }
}
