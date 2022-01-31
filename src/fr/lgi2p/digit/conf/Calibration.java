package fr.lgi2p.digit.conf;

import java.awt.Dimension;


public class Calibration {

    private Configuration configuration; 
    private Dimension drawSize;
    private Dimension tabletSize_mm; 
    private Dimension tabletSize_px;;

    public Calibration() {
        
    }
     
    public void setTabletSize_mm(int w, int h){
        tabletSize_mm = new Dimension(w, h); 

    }
}
