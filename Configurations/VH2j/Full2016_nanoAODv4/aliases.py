import inspect

configurations = os.path.realpath(inspect.getfile(inspect.currentframe())) # this file
configurations = os.path.dirname(configurations) # Full2016_nanoAODv4
configurations = os.path.dirname(configurations) # VH2j
configurations = os.path.dirname(configurations) # Configurations

#aliases = {}

mc = [skey for skey in samples if skey not in ('Fake_em', 'Fake_me', 'DATA')]

bAlgo = 'DeepB'
bWP = '0.2217'

aliases['bVeto'] = {
'expr': '(Sum$(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5 && Jet_btagDeepB[CleanJet_jetIdx] > 0.2217) == 0) && mth > 60'
}

aliases['bVetoDY'] = {                                                                                                              
'expr': '(Sum$(CleanJet_pt > 30. && abs(CleanJet_eta) < 2.5 && Jet_btagDeepB[CleanJet_jetIdx] > 0.2217) == 0) && mth < 60'                       
}

aliases['btag2'] = {
'expr': '(   Alt$(CleanJet_pt[0],0) > 30. \
          && Alt$(CleanJet_pt[1],0) > 30. \
          && ( ( Alt$(abs(CleanJet_eta[0]),99)<2.5 && Alt$(Jet_btagDeepB[CleanJet_jetIdx[0]],0) > 0.2217 ) \
            || ( Alt$(abs(CleanJet_eta[1]),99)<2.5 && Alt$(Jet_btagDeepB[CleanJet_jetIdx[1]],0) > 0.2217 ) ) \
         )' 
}

# Temporary patch for BTV postprocessor bug (no SF for eta < 0, <= 102X_nAODv5_Full2018v5)

btagSFSource = '%s/src/PhysicsTools/NanoAODTools/data/btagSF/DeepCSV_2016LegacySF_V1.csv' % os.getenv('CMSSW_BASE')

aliases['Jet_btagSF_shapeFix'] = {
    'linesToAdd': [
        'gSystem->Load("libCondFormatsBTauObjects.so");',
        'gSystem->Load("libCondToolsBTau.so");',
        'gSystem->AddIncludePath("-I%s/src");' % os.getenv('CMSSW_RELEASE_BASE'),
        '.L %s/patches/btagsfpatch.cc+' % configurations
    ],
    'class': 'BtagSF',
    'args': (btagSFSource,),
    'samples': mc
}

aliases['bVetoSF'] = {
'expr': '( TMath::Exp(Sum$( TMath::Log( (CleanJet_pt>20 && abs(CleanJet_eta)<2.5)*Jet_btagSF_shapeFix[CleanJet_jetIdx]+1*(CleanJet_pt<20 || abs(CleanJet_eta)>2.5) ) ) ) )',
'samples': mc
}

aliases['bVetoSFDY'] = {                                                                                                            
'expr': '( TMath::Exp(Sum$( TMath::Log( (CleanJet_pt>30 && abs(CleanJet_eta)<2.5)*Jet_btagSF_shapeFix[CleanJet_jetIdx]+1*(CleanJet_pt<30 || abs(CleanJet_eta)>2.5) ) ) ) )',
'samples': mc
}                                                                                                                                    


aliases['btag2SF'] = {
'expr': '( ( ( Alt$(CleanJet_pt[0], 0)>30 && Alt$(abs(CleanJet_eta[0]),99)<2.5 )*( Alt$(Jet_btagSF_shapeFix[CleanJet_jetIdx[0]], 1) ) + ( Alt$(CleanJet_pt[0], 0)<30 || Alt$(abs(CleanJet_eta[0]),99)>2.5 ) )* \
           ( ( Alt$(CleanJet_pt[1], 0)>30 && Alt$(abs(CleanJet_eta[1]),99)<2.5 )*( Alt$(Jet_btagSF_shapeFix[CleanJet_jetIdx[1]], 1) ) + ( Alt$(CleanJet_pt[1], 0)<30 || Alt$(abs(CleanJet_eta[1]),99)>2.5 ) ) )\
        ',
'samples': mc
}

aliases['btagSF'] = {
  'expr': '( bVetoSF*bVeto +  bVetoSFDY*bVetoDY + btag2SF*btag2  + ( (!bVeto) && (!bVetoDY) &&  (!btag2) ) )',
'samples': mc
}


systs = ['jes','lf','hf','lfstats1','lfstats2','hfstats1','hfstats2','cferr1','cferr2']

for s in systs:
    aliases['Jet_btagSF_shapeFix_up_%s' % s] = {
        'class': 'BtagSF',
        'args': (btagSFSource, 'up_' + s),
        'samples': mc
    }
    aliases['Jet_btagSF_shapeFix_down_%s' % s] = {
        'class': 'BtagSF',
        'args': (btagSFSource, 'down_' + s),
        'samples': mc
    }
    aliases['btagSF'+s+'up'] = { 'expr': 'bVeto*'+aliases['bVetoSF']['expr'].replace('shapeFix','shapeFix_up_'+s) + '+bVetoDY*'+aliases['bVetoSFDY']\
                                ['expr'].replace('shapeFix','shapeFix_up_'+s) + '+btag2*'+ aliases['btag2SF']['expr'].replace('shapeFix','shapeFix_up_'+s), 'samples':mc  }  
    aliases['btagSF'+s+'down'] = { 'expr': 'bVeto*'+aliases['bVetoSF']['expr'].replace('shapeFix','shapeFix_down_'+s) + '+bVetoDY*'+aliases['bVetoSFDY']\
                                ['expr'].replace('shapeFix','shapeFix_down_'+s) + '+btag2*'+ aliases['btag2SF']['expr'].replace('shapeFix','shapeFix_down_'+s), 'samples':mc  }


