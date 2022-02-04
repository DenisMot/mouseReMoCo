package fr.lgi2p.digit.conf;

import java.awt.Dimension;
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsDevice;
import java.awt.Toolkit;
import java.awt.Insets;
import java.awt.Point;

import javax.swing.JFrame;

public class Calibration {

    public class Layout {
        public int top;
        public int left;
        public int bottom;
        public int right;

        public Layout(int top, int left, int bottom, int right) {
            this.top = top;
            this.left = left;
            this.bottom = bottom;
            this.right = right;
        }

        public int getWidth() {
            return right - left;
        }

        public int getHeight() {
            return bottom - top;
        }
    }

    int screenDiagonal = 0;
    double screenResolution_ppi = 96; // default value for W10 (rather common )
    Layout tabletInScreen;
    Layout screenInTablet;
    Layout screenToDrawing;

    // defines the mapping of the screen to the graphics tablet
    private Dimension screenSize_mm;
    private Dimension screenSize_px;
    private Dimension frameSize_px;
    private Dimension drawingSize_px;
    private Dimension drawingSize_mm;
    public Dimension tabletSize_mm;
    private Dimension tabletSize_px;;

    // tablet values to manually enter in the tablet's driver
    int newTabletTop;
    int newTabletLeft;
    int newTabletBottom;
    int newTabletRight;

    // screen values that we can gather from the JFrame in use
    int tabletOnScreen_top;
    int newScreenLeft;
    int newScreenBottom;
    int newScreenRight;

    boolean doPaintTabletInScreen; 

    Configuration configuration;

    public Calibration(Configuration configuration) {
        doPaintTabletInScreen = true; 
        this.configuration = configuration;
        // tabletSize_mm = new Dimension(0, 0);
        // tabletSize_px = new Dimension(0, 0);
    }

    public void setTabletSize_mm(int w, int h) {
        tabletSize_mm = new Dimension(w, h);
    }

    public void setTabletSize_px(int w, int h) {
        tabletSize_px = new Dimension(w, h);
    }

    public void setScreenDiagonal_mm(int screenDiagonal) {
        this.screenDiagonal = screenDiagonal;
    }

    public void setScreenCalibration(JFrame window) {
        // we need the nesting of the reference frames to determine the active area on
        // the screen:
        // screen -> window -> drawing

        // get the graphic configuration of the device on which sits the window
        GraphicsDevice screen = window.getGraphicsConfiguration().getDevice();
        GraphicsConfiguration screenConfiguration = screen.getDefaultConfiguration();

        Insets screenInsets = Toolkit.getDefaultToolkit().getScreenInsets(screenConfiguration);
        Insets windowInsets = window.getInsets();

        // margins = sum of insets of components (screen + window)
        int screenMarginTop = screenInsets.top + windowInsets.top;
        int screenMarginLeft = screenInsets.left + windowInsets.left;
        int screenMarginBottom = screenInsets.bottom + windowInsets.bottom;
        int screenMarginRight = screenInsets.right + windowInsets.right;

        screenToDrawing = new Layout(screenMarginTop, screenMarginLeft, screenMarginBottom, screenMarginRight);

        // screen characteristics (2 points + 2 lengths)
        int screenHeight = screenConfiguration.getBounds().height;
        int screenWidth = screenConfiguration.getBounds().width;
        int screenLeft = screenConfiguration.getBounds().x;
        int screenTop = screenConfiguration.getBounds().y;
        int screenBottom = screenTop + screenHeight;
        int screenRight = screenLeft + screenWidth;

        // screen limits to be entered in the tablet driver
        tabletOnScreen_top = screenTop + screenMarginTop;
        newScreenLeft = screenLeft + screenMarginLeft;
        newScreenBottom = screenBottom - screenMarginBottom;
        newScreenRight = screenRight - screenMarginRight;

        screenSize_px = new Dimension(screenWidth, screenHeight);

        // below works rarely correctly... very rarely, indeed!
        // int screenResolution_ppi =
        // java.awt.Toolkit.getDefaultToolkit().getScreenResolution();

        // compute screen resolution
        // int screenResolution_ppi = 96;
        if (screenDiagonal > 0) { //
            // simpler :
            // https://en.wikipedia.org/wiki/Pixel_density#Calculation_of_monitor_PPI
            double Hpx = screenConfiguration.getBounds().height;
            double Wpx = screenConfiguration.getBounds().width;
            double Dmm = screenDiagonal;
            double Dpx = Math.sqrt(Wpx * Wpx + Hpx * Hpx);

            // int Hmm = (int) Math.round(Hpx * Dmm / Dpx);
            // int Wmm = (int) Math.round(Wpx * Dmm / Dpx);
            // screenSize_mm = new Dimension(Wmm, Hmm);
            screenResolution_ppi = (int) Math.round(25.4 * Dpx / Dmm);
        }
        // configuration.setMm2px(screenResolution_ppi / 25.4);

        // corresponding screen size in mm
        double w_mm = 25.4 * (double) screenSize_px.width / (double) screenResolution_ppi;
        double h_mm = 25.4 * (double) screenSize_px.height / (double) screenResolution_ppi;
        w_mm = Math.round(w_mm);
        h_mm = Math.round(h_mm);
        screenSize_mm = new Dimension((int) w_mm, (int) h_mm);

        frameSize_px = window.getSize();

        // subtract window insets to get drawing size
        int ww = window.getSize().width; // useful to debug
        int hw = window.getSize().height;
        int wd = ww - (windowInsets.left + windowInsets.right);
        int hd = hw - (windowInsets.top + windowInsets.bottom);
        drawingSize_px = new Dimension(wd, hd);

        // corresponding drawing size in mm
        w_mm = 25.4 * (double) drawingSize_px.width / (double) screenResolution_ppi;
        h_mm = 25.4 * (double) drawingSize_px.height / (double) screenResolution_ppi;
        w_mm = Math.round(w_mm);
        h_mm = Math.round(h_mm);
        drawingSize_mm = new Dimension((int) w_mm, (int) h_mm);

        // int width = window.getSize().width - (windowInsets.left +
        // windowInsets.right);
        // int height = window.getSize().height - (windowInsets.top +
        // windowInsets.bottom);

        configuration.setLinearTask();
    }

    public void paint(java.awt.Graphics g) {
        if (tabletInScreen != null & doPaintTabletInScreen) {
            g.setColor(java.awt.Color.green);

            int width = tabletInScreen.right - tabletInScreen.left;
            int height = tabletInScreen.bottom - tabletInScreen.top;
            int top = tabletInScreen.top - screenToDrawing.top;
            int left = tabletInScreen.left - screenToDrawing.left;
            int bottom = tabletInScreen.bottom - screenToDrawing.top;
            int right = tabletInScreen.right - screenToDrawing.left;

            g.drawRect(left, top, width, height);
            g.drawLine(left, top, right, bottom);
            g.drawLine(left, bottom, right, top);
        }

    }

    private void setNewTabletLimits() {
        if (tabletSize_px != null & tabletSize_mm != null) {
            // find the zone of the screen that corresponds to the tablet
            tabletInScreen = new Layout(0, 0, 0, 0);

            double screen_mm2px = (double) screenSize_px.width / (double) screenSize_mm.width;
            double tablet_mm2px = (double) tabletSize_px.width / (double) tabletSize_mm.width;
            double gain_t2s_px = tablet_mm2px / screen_mm2px;

            double tabletOnScreen_width = ((double) tabletSize_px.width) / gain_t2s_px;
            double tablet_WH_ratio = ((double) tabletSize_px.width) / ((double) tabletSize_px.height);
            double tabletOnScreen_height = tabletOnScreen_width / tablet_WH_ratio;

            double tabletOnDrawing_heightMargin = ((double) drawingSize_px.height - tabletOnScreen_height) / 2.0;
            double tabletOnDrawing_widthMargin = ((double) drawingSize_px.width - tabletOnScreen_width) / 2.0;

            int newScreenHeight = (int) tabletOnScreen_height;
            int newScreenWidth = (int) tabletOnScreen_width;

            // coordinates of the tablet in the drawing (in screen pixel)
            tabletInScreen.top = (int) tabletOnDrawing_heightMargin;
            tabletInScreen.left = (int) tabletOnDrawing_widthMargin;
            tabletInScreen.bottom = tabletInScreen.top + newScreenHeight;
            tabletInScreen.right = tabletInScreen.left + newScreenWidth;

            // coordinates in the screen
            tabletInScreen.top += screenToDrawing.top;
            tabletInScreen.left += screenToDrawing.left;
            tabletInScreen.bottom += screenToDrawing.top;
            tabletInScreen.right += screenToDrawing.left;

            //////////////////////////////////////////////////////////////////////////////////////////////
            // find the zone of the tablet that corresponds to the screen
            screenInTablet = new Layout(0, 0, 0, 0);

            // convert to pixel on tablet
            screenInTablet.top = (int) (tabletInScreen.top * gain_t2s_px);
            screenInTablet.left = (int) (tabletInScreen.left * gain_t2s_px);

            // reverse sign : we want screen in tablet (from tablet in screen)
            screenInTablet.top = -screenInTablet.top;
            screenInTablet.left = -screenInTablet.left;
            // then get the other extremes
            double screenInTablet_width = Math.round(screenSize_px.width * gain_t2s_px);
            double screenInTablet_height = Math.round(screenSize_px.height * gain_t2s_px);
            screenInTablet.bottom = screenInTablet.top + (int) screenInTablet_height;
            screenInTablet.right = screenInTablet.left + (int) screenInTablet_width;

            newScreenWidth = newScreenWidth;
        } 
    }

    public void toWindow() {
        setNewTabletLimits();

        String txt2 = ""; 

        if (tabletSize_px != null & tabletSize_mm != null) {

            double ratio = (double) (tabletInScreen.getWidth()) / (double) (tabletInScreen.getHeight());
            ratio = Math.round(ratio * 1000.0) / 1000.0;
            double ratioSIT = (double) (screenInTablet.getWidth()) / (double) (screenInTablet.getHeight());
            ratioSIT = Math.round(ratioSIT * 1000.0) / 1000.0;

            txt2 =  ";tablet: " + tabletSize_px.width + " x " + tabletSize_px.height + " (pixels)"
            + " = " + tabletSize_mm.width + " x " + tabletSize_mm.height + " (millimeters)"
            + "; ------------------------------------------------------ "
            + "; Zone of screen corresponding to the complete tablet:  "
            + "; top = " + tabletInScreen.top + ", bottom = " + tabletInScreen.bottom
            + "; left = " + tabletInScreen.left + ", right = " + tabletInScreen.right
            + "; Size = " + (tabletInScreen.right - tabletInScreen.left)
            + " x " + (tabletInScreen.bottom - tabletInScreen.top) + " (pixels)" + ", W/H = " + ratio

            + "; Zone of tablet corresponding to the complete screen:   "
            + "; top = " + screenInTablet.top + ", bottom = " + screenInTablet.bottom
            + "; left = " + screenInTablet.left + ", right = " + screenInTablet.right
            + "; Size = " + (screenInTablet.right - screenInTablet.left)
            + " x " + (screenInTablet.bottom - screenInTablet.top) + " (pixels)" + ", W/H = " + ratioSIT
            ;
        } else {
            txt2 =  ";tablet: no information"; 
        }



        String txt = ""
                + ";screen: " + screenSize_px.width + " x " + screenSize_px.height + " (pixels)"
                + " = " + screenSize_mm.width + " x " + screenSize_mm.height + " (millimeters)"
                + ";drawing: " + drawingSize_px.width + " x " + drawingSize_px.height + " (pixels)"
                + " = " + drawingSize_mm.width + " x " + drawingSize_mm.height + " (millimeters)"
                + txt2; 

        String[] info = txt.split(";");

        javax.swing.JOptionPane.showMessageDialog(null, info);

        doPaintTabletInScreen = false;
    }

}
