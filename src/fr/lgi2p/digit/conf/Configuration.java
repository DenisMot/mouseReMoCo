package fr.lgi2p.digit.conf;

import java.awt.AlphaComposite;

import java.awt.Color;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.Font;

import java.awt.Graphics2D;
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsDevice;
import java.awt.GraphicsEnvironment;
import java.awt.Insets;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.image.BufferedImage;
import java.util.Timer;
import java.util.TimerTask;

import javax.swing.JFrame;
// import javax.swing.text.AttributeSet.FontAttribute;

//import fr.lgi2p.digit.Main;
import fr.lgi2p.digit.MainWindow;
import fr.lgi2p.digit.util.Util;
import fr.lgi2p.digit.output.OutputMouse;

public class Configuration {

	// calibration of tablet to display
	public Calibration calibration;

	// command line parameters (with default value)
	private String taskString = "circular";

	// CircularTask
	private CircularTask circularTask;
	private int centerX;
	private int centerY;
	private int cornerX;
	private int cornerY;
	private int externalRadius;
	private int internalRadius;
	private int borderRadius;

	private int circlePerimeter_mm;

	// Auditory Rhythm
	private AuditoryRhythm auditoryRhythm;
	private int halfPeriod = 2000;

	// Linear Task (Guigon 2019 https://pubmed.ncbi.nlm.nih.gov/30649981/)
	private LinearTask linearTask;
	private int interLineDistance_mm = 150;
	private int lineHeight_mm = 100;

	// background and border configuration
	private Color borderColor;
	private Color backgroundColor;
	private Color textColor; 

	// cursor configuration
	private int cursorRadius;
	private Color cursorColorRecord;
	private Color cursorColorWait;
	private Cursor cursorRecord;
	private Cursor cursorWait;
	private Cursor cursorOut;

	// sequence configuration
	private int autoStart; // seconds before auto start
	private int cycleMaxNumber; // Move-Rest cycle number
	private int cycleDuration; // seconds for a Move or Rest (half-cycle duration, in fact...)
	private boolean isTargetHiddenDuringPause = false; 

	// flags
	private boolean isWithLSL = false;
	private boolean isWithPauseTarget = false;

	// state machine
	private String step;

	// Display font
	private int fontSize = 20;
	private Font defaultFont = new Font("Courier", Font.PLAIN, fontSize);;

	// screen configuration (for multiple screens)
	private GraphicsDevice screenDevices[];
	private int usedScreenID;

	// frame configuration
	private Point frameLocation;
	private boolean frameUndecorated = false; // less screen, but can move the window
	private Insets frameInsets; // non drawable part
	private Dimension drawingSize; // usable part of the window
	private Dimension frameSize; // full window size

	///////////////////////////////////////////////////////////////////
	public Configuration() {
		screenDevices = GraphicsEnvironment.getLocalGraphicsEnvironment().getScreenDevices();

		printMonitorSizes();

		// choose screen and set window on this screen
		usedScreenID = selectScreenID() ; 

		setWindowSizeAndLocation();
		printWindowSizeAndLocation();
		setDrawSize();

		calibration = new Calibration(this);

		setDefaultFont();
		setDefaultDoubleCircle();
	}

	private int selectScreenID() {
		// select the last screen that is not main screen (if multiple screens)
		int screenID = 0; // default if only one screen
		screenDevices = GraphicsEnvironment.getLocalGraphicsEnvironment().getScreenDevices();
		for (int i = 0; i < screenDevices.length; i++) {
			GraphicsConfiguration gc = screenDevices[i].getDefaultConfiguration();
			if (!isMainScreen(gc)) {
				screenID = i;
			}
		}
		return screenID; 
	}

	private void setWindowSizeAndLocation() {
		GraphicsConfiguration gc = screenDevices[usedScreenID].getDefaultConfiguration();

		Insets insets = Toolkit.getDefaultToolkit().getScreenInsets(gc);
		Rectangle bounds = gc.getBounds();
		int w = bounds.width;
		int h = bounds.height;

		w -= (insets.left + insets.right);
		h -= (insets.top + insets.bottom);
		this.frameSize = new Dimension(w, h);

		this.frameLocation = new Point(bounds.x + insets.left, bounds.y + insets.top);

	}

	private void printWindowSizeAndLocation() {
		System.out
				.println("Window on screen " + usedScreenID + ": " + frameSize.width + "x" + frameSize.height + " at ("
						+ frameLocation.x + "," + frameLocation.y + ")");
	}

	private boolean isMainScreen(GraphicsConfiguration gc) {
		// the main screen is located at (0,0) = (top, left)
		int x = gc.getBounds().x;
		int y = gc.getBounds().y;
		if (x + y == 0) {
			return true;
		} else {
			return false;
		}
	}

	// private int getMainScreen(GraphicsDevice gd[]) {
	// 	int mainScreen = -1;
	// 	for (int i = 0; i < screenDevices.length; i++) {
	// 		if (isMainScreen(screenDevices[i].getDefaultConfiguration())) {
	// 			mainScreen = i;
	// 		}
	// 	}
	// 	return mainScreen;
	// }

	private String printMonitorSizes() {
		StringBuilder sb = new StringBuilder();

		// get each screen size and insets
		for (int i = 0; i < screenDevices.length; i++) {
			GraphicsConfiguration gc = screenDevices[i].getDefaultConfiguration();

			Insets screenInsets = Toolkit.getDefaultToolkit().getScreenInsets(gc);
			Rectangle screenBounds = gc.getBounds();
			int w = screenBounds.width;
			int h = screenBounds.height;
			w -= (screenInsets.left + screenInsets.right);
			h -= (screenInsets.top + screenInsets.bottom);

			sb.append("screen " + i + ": ");
			sb.append("" + screenBounds.x + ", " + screenBounds.y + ", " + screenBounds.width + ", "
					+ screenBounds.height);
			sb.append(", usable: " + w + "x" + h);
			sb.append(", Insets: " + screenInsets.top + ", " + screenInsets.left + ", " + screenInsets.bottom + ", "
					+ screenInsets.right);
			
			if (isMainScreen(gc)) {
				sb.append(" (Main screen)");
			}
			sb.append("\n");
		}
		System.out.print(sb);
		return sb.toString();
	}

	private void setDrawSize() {
		// build a test frame to get (eventual) insets
		JFrame frame = new JFrame(Consts.APP_NAME);

		frame.setUndecorated(this.frameUndecorated); // false = flexibility to move the window..
		frame.setVisible(true); // frame must be visible to get insets

		this.frameInsets = frame.getInsets();
		this.drawingSize = frame.getSize(); // to create drawSize

		drawingSize.width = this.frameSize.width - (frameInsets.left + frameInsets.right);
		drawingSize.height = this.frameSize.height - (frameInsets.top + frameInsets.bottom);

		frame.dispose();
	}

	private void setDefaultDoubleCircle() {
		// Set default values :
		// draw a double circle in the middle of the screen, with :
		// top-bottom (left-right) margin of 5 * cursorRadius
		// inter-circle distance of 5 * cursorRadius
		// cursor yellow with radius = 16, turning red when recording (darker when out)

		cursorRadius = 16;
		int margin = 5 * cursorRadius;
		externalRadius = (Math.min(drawingSize.height, drawingSize.width) / 2) - margin;

		internalRadius = externalRadius - margin;
		borderRadius = 1;
		borderColor = Util.toColor("white");
		textColor = Util.toColor("white");
		backgroundColor = Util.toColor("black");
		autoStart = 3600;
		cycleDuration = 20;
		cycleMaxNumber = 6;

		cursorColorRecord = Util.toColor("red");
		cursorColorWait = Util.toColor("yellow");

		// once done, then set corner (and center)
		setCornerX(drawingSize.width / 2 - externalRadius);
		setCornerY(drawingSize.height / 2 - externalRadius);

		// and set cursors (also done in double circle constructor = if command line)
		setCursorRecord();
		setCursorWait();

		// and set index of difficulty corresponding to the defaults
		setCircularTask();

		setLinearTask();
	}

	public static class Line {
		public int x1;
		public int y1;
		public int x2;
		public int y2;
		public Color color;

		public Line(int x1, int y1, int x2, int y2, Color color) {
			this.x1 = x1;
			this.y1 = y1;
			this.x2 = x2;
			this.y2 = y2;
			this.color = color;
		}

		public void rotate(double alpha) {
			double cos_ = Math.cos(alpha); // shorter
			double sin_ = Math.sin(alpha);

			double X1 = x1 * cos_ - y1 * sin_;
			double Y1 = x1 * sin_ + y1 * cos_;
			double X2 = x2 * cos_ - y2 * sin_;
			double Y2 = x2 * sin_ + y2 * cos_;

			x1 = (int) Math.round(X1);
			y1 = (int) Math.round(Y1);
			x2 = (int) Math.round(X2);
			y2 = (int) Math.round(Y2);
		}

		public void translate(int dx, int dy) {
			x1 = x1 + dx;
			y1 = y1 + dy;
			x2 = x2 + dx;
			y2 = y2 + dy;
		}

		@Override
		public String toString() {
			String  Txt = "[x1="+x1+",y1="+y1+",x2="+x2+",y2="+y2+"]" ; 
			return Txt;
		}
	}

	public void writeBeep() {
		if (MainWindow.getInstance() != null) {
			OutputMouse outputMouse = MainWindow.getInstance().getOutputMouse();
			if (outputMouse != null) {
				if (MainWindow.getInstance().isRecording()) {
					outputMouse.writeMarker("Beep");
				}
			}
		}
	}

	public class AuditoryRhythm {
		private Timer beepBeep = null;
		private TimerTask playBeep = null;

		private Line[] targetLines;

		public AuditoryRhythm(int x) {
			halfPeriod = x;
			beepBeep = new Timer();
			playBeep = new TimerTask() {
				@Override
				public void run() {
					java.awt.Toolkit.getDefaultToolkit().beep();
					writeBeep();
				}
			};
			startBeep();
			if (taskString.equals("circular")) {
				setTargetLines();
			}

		}

		public void startBeep() {
			long initialDelay = 3000L; // we need sometimes to initialize the app
			beepBeep.scheduleAtFixedRate(playBeep, initialDelay, halfPeriod);
		}

		public void stopBeep() {
			if (beepBeep != null) {
				beepBeep.cancel();
			}
		}

		public void setTargetLines() {
			if (taskString.equals("circular")) {
				int w = 5 * cursorRadius;

				targetLines = new Line[2];
				targetLines[0] = new Line(
						centerX, centerY - (externalRadius + w),
						centerX, centerY - (internalRadius - w),
						Color.GRAY);
				targetLines[1] = new Line(
						centerX, centerY + (externalRadius + w),
						centerX, centerY + (internalRadius - w),
						Color.GRAY);
			}
		}

		public Line[] getTargetLines() {
			return targetLines;
		}

	}

	public AuditoryRhythm getAuditoryRhythm() {
		return auditoryRhythm;
	}

	public void setHalfPeriod(int halfPeriod) {
		if (auditoryRhythm != null) {
			auditoryRhythm.stopBeep();
		}
		auditoryRhythm = new AuditoryRhythm(halfPeriod);
	}

	public class LinearTask {
		private Line lineRight = null;
		private Line lineLeft = null;
		private Line diagonal = null;
		private double mm2px = 0; 

		public LinearTask() {
			// the elements on the screen are all relative to the center
			// DECISION: the center of the screen is the origin of the coordinates on the
			// screen
			// the diagonal is a rotation around the center of the screen
			// DECISION: we compute the display as horizontal, then rotate it to the
			// diagonal
			// distances in mm (tablet) must be translated into pixels to display (screen)
			// DECISION: we multiply distances in mm by the gain (mm2px: same along x and y)

			mm2px = calibration.screenResolution_ppi / Consts.INCH_PER_MM;

			// to draw something is no screen calibration is provided
			if (calibration.screenResolution_ppi == 0)
				mm2px = 96 / Consts.INCH_PER_MM;

			Double lineHalfHeight = mm2px * lineHeight_mm / 2.0;
			Double lineHalfDistance = mm2px * interLineDistance_mm / 2.0;

			int x1 = (int) Math.round(lineHalfDistance);
			int y1 = (int) Math.round(lineHalfHeight);

			lineRight = new Line(x1, y1, x1, -y1, borderColor);
			lineLeft = new Line(-x1, y1, -x1, -y1, borderColor);

			// default to use the diagonal of the drawing
			int H = drawingSize.height;
			int W = drawingSize.width;

			// if a tablet is calibrated, then use it
			if (calibration != null & calibration.tabletSize_mm != null) {
				H = calibration.tabletSize_mm.height;
				W = calibration.tabletSize_mm.width;
			}
			H = -H; // Y axis is reversed in java

			double alpha = Math.atan2(H, W); // diagonal angle
			lineLeft.rotate(alpha);
			lineRight.rotate(alpha);

			lineLeft.translate(centerX, centerY);
			lineRight.translate(centerX, centerY);

			// computation of coordinates as for the left and right lines
			diagonal = new Line(-drawingSize.width / 2, 0, drawingSize.width / 2, 0, Color.GRAY);
			diagonal.rotate(alpha); 
			diagonal.translate(centerX, centerY);
		}

		public Line getLineLeft() {
			return lineLeft;
		}

		public Line getLineRight() {
			return lineRight;
		}

		public Line getDiagonal() {
			return diagonal;
		}

		public double getMm2px() {
			return mm2px;
		}
	}

	public void setLinearTask() {
		linearTask = new LinearTask();
	}

	public LinearTask getLinearTask() {
		return linearTask;
	}

	public class CircularTask {
		public double radius;

		public int tolerance_px; // must be integer (pixel)
		public double ID;
		public double perimeter;

		public int internalLimit = internalRadius + cursorRadius;
		public int externalLimit = externalRadius - cursorRadius - borderRadius;

		public CircularTask() {
			setPublicTaskValues(); // not much to do, but initializing...

		}

		private void setPublicTaskValues() {
			// limits of the path
			internalLimit = internalRadius + cursorRadius;
			externalLimit = externalRadius - cursorRadius - borderRadius;

			// ID in the steering law (Accot & Zhai 1999)
			radius = (internalLimit + externalLimit) / 2.0;
			tolerance_px = externalLimit - internalLimit;
			perimeter = 2.0 * Math.PI * radius;
			ID = perimeter / (double) tolerance_px;
		}

		public void setIndexOfDifficulty(double indexOfDifficulty) {
			// we shall change the internal circle to be as close as possible to the
			// requested ID

			// from the steering law:
			// ID = average distance per circle / between-circle width
			// We set :
			// R = external limit
			// w = half of between-circle width
			// It comes:
			// average distance per circle = 2 oi (R - w)
			// between-circle width = 2 w
			// Simple math give :
			// ID = 2 pi (R - w) / 2 w
			// ID = (pi R - pi w) / w
			// w ID = pi R - pi w
			// w ID + pi w = pi R
			// w (ID + pi) = pi R
			// w = (pi R) / (ID + pi)

			double w; // target size
			int Wn; // target size rounded to pixel

			w = (Math.PI * externalLimit) / (indexOfDifficulty + Math.PI);
			Wn = (int) Math.round(2 * w);
			// with the new target width Wn, we change the internal limit
			internalLimit = externalLimit - Wn;
			// and we set the novel radius of the internal circle
			internalRadius = internalLimit - cursorRadius;

			// now, we can set the (novel) index of difficulty etc.
			setPublicTaskValues();
		}

		public void setCirclePerimeter() {
			if (Configuration.this.circlePerimeter_mm > 0 & calibration.screenResolution_ppi > 0.0) {
				perimeter = (double) Configuration.this.circlePerimeter_mm;
				perimeter = perimeter * calibration.screenResolution_ppi / Consts.INCH_PER_MM;
				radius = perimeter / (2.0 * Math.PI);
				double tolerance = perimeter / ID;
	
				double externalLimit_ = radius + tolerance / 2.0;
				double internalLimit_ = radius - tolerance / 2.0;
	
				double externalRadius_ = externalLimit_ + cursorRadius;
				double internalRadius_ = internalLimit_ - cursorRadius;
	
				// border is inside the circle
				externalRadius_ = externalRadius_ + borderRadius;
	
				externalRadius = (int) Math.round(externalRadius_);
				internalRadius = (int) Math.round(internalRadius_);
	
				setCornerX(drawingSize.width / 2 - externalRadius);
				setCornerY(drawingSize.height / 2 - externalRadius);
	
				externalLimit = (int) Math.round(externalLimit_);
				internalLimit = (int) Math.round(internalLimit_);
	
				tolerance_px = externalLimit - internalLimit;
	
				ID = perimeter / (double) tolerance_px;
			}
		}
	}


	public void setCirclePerimeter_mm(int perimeter) {
		this.circlePerimeter_mm = perimeter;
	}

	public CircularTask getCircularTask() {
		return circularTask;
	}

	public void setCircularTask() {
		circularTask = new CircularTask();
	}

	public void setIndexOfDifficulty(double indexOfDifficulty) {
		// TODO : direct call to circularTask ?
		circularTask.setIndexOfDifficulty(indexOfDifficulty);
	}

	public double getIndexOfDifficulty() {
		return circularTask.ID;
	}

	public int getCycleDuration() {
		return cycleDuration;
	}

	public void setCycleDuration(int cycleDuration) {
		this.cycleDuration = cycleDuration;
	}

	public int getCycleMaxNumber() {
		return cycleMaxNumber;
	}

	public void setCycleMaxNumber(int cycleMax) {
		this.cycleMaxNumber = cycleMax;
	}

	private Cursor createCursor(int cursorRadius, Color cursorColor) {
		Toolkit toolkit = Toolkit.getDefaultToolkit();

		int CursorDiameter = cursorRadius * 2;

		// get cursor acceptable size for the OS
		Dimension cursorSizeOS = toolkit.getBestCursorSize(CursorDiameter, CursorDiameter);

		if (cursorSizeOS.height < CursorDiameter) {
			// resize the cursor to what is possible for this OS...
			CursorDiameter = Math.min(CursorDiameter, cursorSizeOS.height);
			// ... and inform that you did so
			this.cursorRadius = CursorDiameter / 2;
			System.out.println("Closest possible cursor size for this system is " + cursorSizeOS.width + "x"
					+ cursorSizeOS.height);
		}

		// create an image with a transparent background + a circle with hotspot in the
		// middle
		// TYPE_INT_ARGB to allow transparency
		BufferedImage bufferedImage = new BufferedImage(cursorSizeOS.height, cursorSizeOS.height,
				BufferedImage.TYPE_INT_ARGB);

		Graphics2D g2d = bufferedImage.createGraphics();
		// transparent background color (size accepted by OS)
		g2d.setComposite(AlphaComposite.Clear);
		g2d.fillRect(0, 0, cursorSizeOS.height, cursorSizeOS.height);
		g2d.setComposite(AlphaComposite.Src);
		// circle with color (size acceptable by OS AND user)
		g2d.setColor(cursorColor);
		g2d.fillOval(0, 0, CursorDiameter, CursorDiameter);

		Point hotspot = new Point(CursorDiameter / 2, CursorDiameter / 2);
		int d = 2;
		g2d.setColor(backgroundColor);
		g2d.drawLine(hotspot.x - d, hotspot.y, hotspot.x + d, hotspot.y);
		g2d.drawLine(hotspot.x, hotspot.y - d, hotspot.x, hotspot.y + d);

		g2d.dispose();

		return toolkit.createCustomCursor(bufferedImage, hotspot, "MyCursor");

	}

	public Point getFrameLocation() {
		return frameLocation;
	}

	public void setCursorWait() {
		this.cursorWait = createCursor(cursorRadius, cursorColorWait);
	}

	public Cursor getCursorWait() {
		return cursorWait;
	}

	public void setCursorRecord() {
		this.cursorRecord = createCursor(cursorRadius, cursorColorRecord);
		this.cursorOut = createCursor(cursorRadius, cursorColorRecord.darker().darker());
	}

	public Cursor getCursorOut() {
		return cursorOut;
	}

	public Cursor getCursorRecord() {
		return cursorRecord;
	}

	public Dimension getFrameSize() {
		return this.frameSize;
	}

	public void setFrameSize(Dimension frameSize) {
		this.frameSize = frameSize;
	}

	public int getCenterX() {
		return centerX;
	}

	public int getCenterY() {
		return centerY;
	}

	public void setCenterX(int centerX) {
		this.centerX = centerX;
		this.cornerX = centerX - externalRadius; // set the corner as well
		System.out.println("cornerX = " + this.getCornerX() + ", centerX = " + centerX + ", externalRadius ="
				+ this.getExternalRadius());
	}

	public void setCenterY(int centerY) {
		this.centerY = centerY;
		this.cornerY = centerY - externalRadius; // set the corner as well
		System.out.println("cornerY = " + this.getCornerY() + ", centerY = " + centerY + ", externalRadius ="
				+ this.getExternalRadius());
	}

	public int getCornerX() {
		return cornerX;
	}

	public void setCornerX(int cornerX) {
		this.cornerX = cornerX;
		this.centerX = cornerX + this.externalRadius;
	}

	public int getCornerY() {
		return cornerY;
	}

	public void setCornerY(int cornerY) {
		this.cornerY = cornerY;
		this.centerY = cornerY + this.getExternalRadius();
	}

	public int getExternalRadius() {
		return externalRadius;
	}

	public void setExternalRadius(int externalRadius) {
		this.externalRadius = externalRadius;
		// this.radiusExternalLimit = externalRadius - cursorRadius - borderRadius;
		setCircularTask();
	}

	public int getInternalRadius() {
		return internalRadius;
	}

	public void setInternalRadius(int internalRadius) {
		this.internalRadius = internalRadius;
		// this.radiusInternalLimit = internalRadius + cursorRadius;
		setCircularTask();
	}

	public int getBorderRadius() {
		return borderRadius;
	}

	public void setBorderRadius(int border) {
		this.borderRadius = border;
		setCircularTask();
	}

	public Color getBorderColor() {
		return borderColor;
	}

	public void setBorderColor(Color borderColor) {
		this.borderColor = borderColor;
	}

	public Color getTextColor() {
		return textColor;
	}
	
	public void setTextColor(Color textColor) {
		this.textColor = textColor;
	}
	public Color getBackgroundColor() {
		return backgroundColor;
	}

	public void setBackgroundColor(Color backgroundColor) {
		this.backgroundColor = backgroundColor;
	}

	public int getAutoStart() {
		return autoStart;
	}

	public void setAutoStart(int autoStart) {
		this.autoStart = autoStart;
	}

	public int getCursorRadius() {
		return cursorRadius;
	}

	public void setCursorRadius(int cursorRadius) {
		this.cursorRadius = cursorRadius;
		setCircularTask();
	}

	public Color getCursorColorRecord() {
		return cursorColorRecord;
	}

	public void setCursorColorRecord(Color cursorColorRecord) {
		this.cursorColorRecord = cursorColorRecord;
	}

	public Color getCursorColorWait() {
		return cursorColorWait;
	}

	public void setCursorColorWait(Color cursorColorWait) {
		this.cursorColorWait = cursorColorWait;
	}

	public String getStep() {
		return step;
	}

	public void setStep(String step) {
		this.step = step;
	}

	public void setDefaultValues(String step) {
		this.step = step;
	}

	public void toWindow() {
		String[] configurationInfo = this.toString().split(";");

		javax.swing.JOptionPane.showMessageDialog(null, configurationInfo);

	}

	@Override
	public String toString() {
		// we separate field-value pairs using ; and field from value using space
		// REASON : we cannot use , and = that appear in java colors :
		// java.awt.Color[r=255,g=255,b=255]
		String Txt = "software " + Consts.APP_NAME + ";version " + Consts.APP_VERSION + ";isWithLSL " + isWithLSL
				+ ";screenWidth " + drawingSize.width + ";screenHeight " + drawingSize.height
				+ ";centerX " + centerX + ";centerY " + centerY
				+ ";autoStart " + autoStart + ";cycleMaxNumber " + cycleMaxNumber + ";cycleDuration " + cycleDuration
				+ ";borderColor " + borderColor + ";textColor " + textColor + ";backgroundColor " + backgroundColor 
				+ ";cursorColorRecord " + cursorColorRecord + ";cursorColorWait " + cursorColorWait
				+ ";task " + taskString
				;
		if (taskString.equals("circular")) {
			Txt = Txt + ";cornerX " + cornerX + ";cornerY " + cornerY 
					+ ";externalRadius " + externalRadius + ";internalRadius " + internalRadius 
					+ ";borderRadius " + borderRadius + ";cursorRadius " + cursorRadius
					+ ";indexOfDifficulty " + circularTask.ID 
					+ ";taskRadius " + circularTask.radius 
					+ ";taskTolerance " + circularTask.tolerance_px
					;
		}
		if (taskString.equals("linear")) {
			Txt = Txt + ";interLineDistance_mm " + interLineDistance_mm + ";lineHeight_mm " + lineHeight_mm 
					+ ";mm2px " + linearTask.getMm2px()
					+ ";Diagonal " + linearTask.getDiagonal()
					+ ";LineLeft " + linearTask.getLineLeft() 
					+ ";LineRight " + linearTask.getLineRight(); 
					;
			
		}
		if (auditoryRhythm != null) {
			Txt = Txt + ";halfPeriod " + halfPeriod;
		}
		// System.out.println(Txt);
		return Txt;
	}

	public void printConfiguration() {
		String[] configurationInfo = this.toString().split(";");
		for (int i = 0; i < configurationInfo.length; i++) {
			String[] configurationKeyValue = configurationInfo[i].split(" ");
			System.out.println(configurationKeyValue[0] +" = "+ configurationKeyValue[1]);
		}
	}
	
	public Insets getFrameInsets() {
		return frameInsets;
	}

	public boolean getFrameUndecorated() {
		return frameUndecorated;
	}

	public boolean isWithLSL() {
		return isWithLSL;
	}

	public void setWithLSL(boolean isWithLSL) {
		this.isWithLSL = isWithLSL;
	}

	public void setWithPauseTarget(boolean isWithPauseTarget) {
		this.isWithPauseTarget = isWithPauseTarget;
	}

	public boolean isWithPauseTarget() {
		return isWithPauseTarget;
	}

	public void setInterLineDistance_mm(int interLineDistance_mm) {
		this.interLineDistance_mm = interLineDistance_mm;
		setLinearTask();
	}

	public void setLineHeight_mm(int lineHeight_mm) {
		this.lineHeight_mm = lineHeight_mm;
		setLinearTask();
	}

	public String getTaskString() {
		return taskString;
	}

	public void setTaskString(String taskString) {
		this.taskString = taskString;
	}

	public void setDefaultFont() {
		// set a font proportional to screen size to preserve legibility
		// take care of screen with different aspect ratio
		fontSize = Math.min(frameSize.width / 72, frameSize.height / 45);

		defaultFont = new Font("Courier", Font.PLAIN, fontSize);
		System.out.println("Default font: " + defaultFont);
	}

	public Font getDefaultFont() {
		return defaultFont;
	}

	public void setTabletSize_mm(int w, int h) {

	}

	public boolean isTargetHiddenDuringPause() {
		return isTargetHiddenDuringPause;
	}

}
