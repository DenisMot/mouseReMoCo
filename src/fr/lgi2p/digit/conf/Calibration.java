package fr.lgi2p.digit.conf;

import java.awt.Dimension;
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsDevice;
import java.awt.Toolkit;
import java.awt.Insets;

import javax.swing.JFrame;

import fr.lgi2p.digit.MainWindow;

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
    double screenResolution_ppi = 0; //72.0; // default value for W10 = 96 (rather common )
    double tabletResolution_ppi; 

    Layout tabletInScreen;
    Layout screenInTablet;
    Layout screenToDrawing;

    // defines the mapping of the screen to the graphics tablet
    private Dimension screenSize_mm;
    private Dimension screenSize_px;
    private Dimension drawingSize_px;
    private Dimension drawingSize_mm;
    public Dimension tabletSize_mm;
    private Dimension tabletSize_px;;

    // screen values that we can gather from the JFrame in use
    int tabletOnScreen_top;
    int newScreenLeft;
    int newScreenBottom;
    int newScreenRight;

    // flag to paint the tablet on the screen
    boolean flagPaintTabletInScreen;

    Configuration configuration;

    public Calibration(Configuration configuration) {
        flagPaintTabletInScreen = true;
        this.configuration = configuration;
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

    public void setScreenSize_mm(int w, int h) {
        screenSize_mm = new Dimension(w, h);
    }
    public void setScreenCalibration(JFrame window) {
        // we need the nesting of the reference frames to determine the active area on
        // the screen: screen -> window -> drawing

        // get the graphic configuration of the device on which the window is located
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

        // screen resolution
        // the code below rarely works correctly... very rarely, indeed!
        // screenResolution_ppi = java.awt.Toolkit.getDefaultToolkit().getScreenResolution();

        // compute screen resolution (if we have the diagonal on the cli)
        if (screenDiagonal > 0) {
            // https://en.wikipedia.org/wiki/Pixel_density#Calculation_of_monitor_PPI
            double Hpx = screenConfiguration.getBounds().height;
            double Wpx = screenConfiguration.getBounds().width;
            double Dmm = screenDiagonal;
            double Dpx = Math.sqrt(Wpx * Wpx + Hpx * Hpx);
            screenResolution_ppi = Consts.INCH_PER_MM * Dpx / Dmm;
        }

        // screen size in pixels
        int screenHeight = screenConfiguration.getBounds().height;
        int screenWidth = screenConfiguration.getBounds().width;
        screenSize_px = new Dimension(screenWidth, screenHeight);

        // subtract window insets to get drawing size
        int ww = window.getSize().width; // useful to debug
        int hw = window.getSize().height;
        int wd = ww - (windowInsets.left + windowInsets.right);
        int hd = hw - (windowInsets.top + windowInsets.bottom);
        drawingSize_px = new Dimension(wd, hd);

        if (screenDiagonal > 0) {
            // corresponding screen size in mm
            double w_mm = Consts.INCH_PER_MM * (double) screenSize_px.width / screenResolution_ppi;
            double h_mm = Consts.INCH_PER_MM * (double) screenSize_px.height / screenResolution_ppi;
            w_mm = Math.round(w_mm);
            h_mm = Math.round(h_mm);
            screenSize_mm = new Dimension((int) w_mm, (int) h_mm);

            // corresponding drawing size in mm
            w_mm = Consts.INCH_PER_MM * (double) drawingSize_px.width / screenResolution_ppi;
            h_mm = Consts.INCH_PER_MM * (double) drawingSize_px.height / screenResolution_ppi;
            w_mm = Math.round(w_mm);
            h_mm = Math.round(h_mm);
            drawingSize_mm = new Dimension((int) w_mm, (int) h_mm);
        }

        // rebuild the task with the new calibration
        configuration.setLinearTask();
        configuration.getCircularTask().setCirclePerimeter(); 
        configuration.getAuditoryRhythm().setTargetLines();
    }

    public void paint(java.awt.Graphics g) {
        if (tabletInScreen != null & flagPaintTabletInScreen) {
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

    private void setMappingBetweenScreenAndTablet() {
        // define the mapping between screen and tablet
        // nothing todo if there is no tablet...
        if (tabletSize_px != null & tabletSize_mm != null) {
            tabletInScreen = zoneOfScreenCorrespondingToTablet();
            screenInTablet = zoneOfTabletCorrespondingToScreen();
        }
    }

    private Layout zoneOfScreenCorrespondingToTablet() {
        // define the zone of the screen that corresponds to the tablet
        double screen_mm2px = (double) screenSize_px.width / (double) screenSize_mm.width;
        double tablet_mm2px = (double) tabletSize_px.width / (double) tabletSize_mm.width;
        double gain_t2s_px = tablet_mm2px / screen_mm2px;

        double tabletOnScreen_width = ((double) tabletSize_px.width) / gain_t2s_px;
        double tablet_WH_ratio = ((double) tabletSize_px.width) / ((double) tabletSize_px.height);
        double tabletOnScreen_height = tabletOnScreen_width / tablet_WH_ratio;

        double tabletOnDrawing_heightMargin = ((double) drawingSize_px.height - tabletOnScreen_height) / 2.0;
        double tabletOnDrawing_widthMargin = ((double) drawingSize_px.width - tabletOnScreen_width) / 2.0;

        Layout tabletInScreen = new Layout(0, 0, 0, 0);
        // coordinates of the tablet in the drawing (in screen pixel)
        tabletInScreen.top = (int) Math.round(tabletOnDrawing_heightMargin);
        tabletInScreen.left = (int) Math.round(tabletOnDrawing_widthMargin);
        tabletInScreen.bottom = (int) Math.round(tabletOnDrawing_heightMargin + tabletOnScreen_height);
        tabletInScreen.right = (int) Math.round(tabletOnDrawing_widthMargin + tabletOnScreen_width);

        // coordinates in the screen
        tabletInScreen.top += screenToDrawing.top;
        tabletInScreen.left += screenToDrawing.left;
        tabletInScreen.bottom += screenToDrawing.top;
        tabletInScreen.right += screenToDrawing.left;

        return tabletInScreen;
    }

    private Layout zoneOfTabletCorrespondingToScreen() {
        // define the zone of the tablet that corresponds to the screen
        double screen_mm2px = (double) screenSize_px.width / (double) screenSize_mm.width;
        double tablet_mm2px = (double) tabletSize_px.width / (double) tabletSize_mm.width;
        double gain_t2s_px = tablet_mm2px / screen_mm2px;

        Layout screenInTablet = new Layout(0, 0, 0, 0);

        // set gain: convert to pixel size on the tablet
        screenInTablet.top = (int) (tabletInScreen.top * gain_t2s_px);
        screenInTablet.left = (int) (tabletInScreen.left * gain_t2s_px);

        // set orientation : reverse sign (screenInTablet = - tabletInScreen)
        screenInTablet.top = -screenInTablet.top;
        screenInTablet.left = -screenInTablet.left;

        // then get the other extremes
        double screenInTablet_width = Math.round(screenSize_px.width * gain_t2s_px);
        double screenInTablet_height = Math.round(screenSize_px.height * gain_t2s_px);
        screenInTablet.bottom = screenInTablet.top + (int) screenInTablet_height;
        screenInTablet.right = screenInTablet.left + (int) screenInTablet_width;

        return screenInTablet;
    }

    private double diagonal(Dimension d) {
        int w = d.width; 
        int h = d.height; 
        return Math.round(Math.sqrt(w*w + h*h)); 
    }

    public void toWindow() {
        setMappingBetweenScreenAndTablet();

        // set minimal information (if no calibration at all)
        String displaySizeMessage = ""
                + ";screen: " + screenSize_px.width + " x " + screenSize_px.height + " (pixels)"
                + ";drawing: " + drawingSize_px.width + " x " + drawingSize_px.height + " (pixels)";

        // if screen has been calibrated ( = we know the diagonal)
        String screenCalibrationMessage = ";screen: no calibration";
        if (screenSize_mm != null) {
            double screenDiagonal_mm = diagonal(screenSize_mm); 
            double screenDiagonal_inch = screenDiagonal_mm / Consts.INCH_PER_MM;
            screenCalibrationMessage = ""
                + ";screen (" + String.format("%5.2f\", %3.0fmm", screenDiagonal_inch, screenDiagonal_mm) + "): "
                + "" + screenSize_mm.width + "x" + screenSize_mm.height + " mm"
                + ";screen = " + screenSize_px.width + " x " + screenSize_px.height + " (pixels)"
                + String.format(" @ %5.2fdpi",screenResolution_ppi)
                + ";drawing: "
                + "" + drawingSize_mm.width + " x " + drawingSize_mm.height + " (mm)"
                + " = " + drawingSize_px.width + " x " + drawingSize_px.height + " (pixels)";
                ;
        } 

        // if tablet has been calibrated
        String tabletCalibrationMessage = ";tablet: no calibration";
        if (tabletSize_px != null & tabletSize_mm != null) {
            double ratioTabletInScreen = (double) (tabletInScreen.getWidth()) / (double) (tabletInScreen.getHeight());
            double ratioScreenInTablet = (double) (screenInTablet.getWidth()) / (double) (screenInTablet.getHeight());

            double tabletDiagonal_mm = diagonal(tabletSize_mm);
            double tabletDiagonal_inch = tabletDiagonal_mm / Consts.INCH_PER_MM;
            tabletResolution_ppi = diagonal(tabletSize_px) / tabletDiagonal_inch; 
            tabletCalibrationMessage = ""
                    + ";tablet (" + String.format("%5.2f\", %3.0fmm", tabletDiagonal_inch, tabletDiagonal_mm) + "): "
                    + "" + tabletSize_mm.width + "x" + tabletSize_mm.height + " mm"
                    + " = " + tabletSize_px.width + " x " + tabletSize_px.height + " (pixels)"
                    + String.format(" @ %5.2fdpi",tabletResolution_ppi)

                    + "; ------------------------------------------------------ "
                    + "; Area of the screen corresponding to the complete tablet:  "
                    + "; top = " + tabletInScreen.top + ", bottom = " + tabletInScreen.bottom
                    + "; left = " + tabletInScreen.left + ", right = " + tabletInScreen.right
                    + "; Size = " + (tabletInScreen.right - tabletInScreen.left)
                    + " x " + (tabletInScreen.bottom - tabletInScreen.top) + " (pixels)" + ", W/H = "
                    + String.format("%5.3f", ratioTabletInScreen)
                    + "; ------------------------------------------------------ "
                    + "; Area of the tablet corresponding to the complete screen:   "
                    + "; top = " + screenInTablet.top + ", bottom = " + screenInTablet.bottom
                    + "; left = " + screenInTablet.left + ", right = " + screenInTablet.right
                    + "; Size = " + (screenInTablet.right - screenInTablet.left)
                    + " x " + (screenInTablet.bottom - screenInTablet.top) + " (pixels)" + ", W/H = "
                    + String.format("%5.3f", ratioScreenInTablet)
                    ;
        }

        String messageDialog =  screenCalibrationMessage + tabletCalibrationMessage;

        String[] info = messageDialog.split(";");

        javax.swing.JOptionPane.showMessageDialog(null, info);

        // we can remove the display of the tablet on the screen
        flagPaintTabletInScreen = false;

        // make the app window active 
        // https://stackoverflow.com/questions/641172/how-to-focus-a-jframe
        JFrame frame = MainWindow.getInstance().getFrame(); 
        frame.setVisible(true);
        frame.toFront();
        frame.requestFocus();
    }

}
