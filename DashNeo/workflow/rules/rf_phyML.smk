checkpoint rf_phyML: 
   input: 
      expand(
         "results/rf/{position}.{feature}.rf_ete", 
         position = POS, 
         feature=feature_names
      )
   output: 
      "results/rf_phyML.csv"
   script: 
      "../scripts/rfAfterPhyML.py"
