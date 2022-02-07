package fr.lgi2p.digit;

import java.util.LinkedHashMap;
import java.util.logging.Logger;

import fr.lgi2p.digit.conf.Configuration;
import fr.lgi2p.digit.conf.Consts;
import fr.lgi2p.digit.util.Util;

public class Main {

	private static final Logger logger = Util.getLogger(Main.class);

	public static void main(String[] args) {
		logBasicSystemInfo();
		Configuration configuration = new Configuration();

		parseArguments(args, configuration);

		showMainWindow(configuration);
		logger.info("End of Main...");
	}

	private static void parseArguments(String[] args, Configuration configuration) {

		LinkedHashMap<String, String> arguments = buildArgumentsHashMap(args);

		// read arguments
		for (String key : arguments.keySet()) {

			if ("-cornerX".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				// Args.checkForRange(value, 0, 4000);
				configuration.setCornerX(value);
			}
			if ("-cornerY".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				// Args.checkForRange(value, 0, 3000);
				configuration.setCornerY(value);
			}
			if ("-externalRadius".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				// Args.checkForRange(value, 1, configuration.getCornerX() * 2);
				configuration.setExternalRadius(value);
			}
			if ("-internalRadius".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				// Args.checkForRange(value, 1, configuration.getExternalRadius()*2);
				configuration.setInternalRadius(value);
			}
			if ("-borderRadius".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				// Args.checkForRange(value, 1, 20);
				configuration.setBorderRadius(value);
			}
			if ("-borderColor".equalsIgnoreCase(key)) {
				String value = arguments.get(key);
				// Args.checkForColor(value);
				configuration.setBorderColor(Util.toColor(value));
			}
			if ("-backgroundColor".equalsIgnoreCase(key)) {
				String value = arguments.get(key);
				// Args.checkForColor(value);
				configuration.setBackgroundColor(Util.toColor(value));
			}
			if ("-autoStart".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				// Args.checkForRange(value, -1, 1000);
				configuration.setAutoStart(value);
			}
			if ("-cursorRadius".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setCursorRadius(value);
			}
			if ("-cursorColorRecord".equalsIgnoreCase(key)) {
				String value = arguments.get(key);
				configuration.setCursorColorRecord(Util.toColor(value));
			}
			if ("-cursorColorWait".equalsIgnoreCase(key)) {
				String value = arguments.get(key);
				// Args.checkForColor(value);
				configuration.setCursorColorWait(Util.toColor(value));
			}
			if ("-centerX".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setCenterX(value);
			}
			if ("-centerY".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setCenterY(value);
			}
			if ("-cycleMaxNumber".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setCycleMaxNumber(value);
			}
			if ("-cycleDuration".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setCycleDuration(value);
			}
			if ("-indexOfDifficulty".equalsIgnoreCase(key)) {
				double value = Double.parseDouble(arguments.get(key));
				configuration.setIndexOfDifficulty(value);
			}
			if ("-task".equalsIgnoreCase(key)) {
				String value = arguments.get(key);
				configuration.setTaskString(value);
			}
			if ("-interLineDistance_mm".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setInterLineDistance_mm(value);
			}
			if ("-lineHeight_mm".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setLineHeight_mm(value);
			}			
			if ("-circlePerimeter_mm".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setCirclePerimeter_mm(value);
			}
			// if ( "-mm2px".equalsIgnoreCase(key) ) {
			// double value = Double.parseDouble(arguments.get(key));
			// configuration.setMm2px(value);
			// }
			if ("-halfPeriod".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				configuration.setHalfPeriod(value);
			}
			if ("-tabletSize".equalsIgnoreCase(key)) {
				String value = arguments.get(key);
				// we treat x and = as equivalent separators (only order matters)
				String[] txt = value.toString().split("=|x");
				int w_mm = Util.toInt(txt[0]);
				int h_mm = Util.toInt(txt[1]);
				int w_px = Util.toInt(txt[2]);
				int h_px = Util.toInt(txt[3]);
				if (configuration.calibration != null) {
					configuration.calibration.setTabletSize_mm(w_mm, h_mm);
					configuration.calibration.setTabletSize_px(w_px, h_px);
				}
			}
			if ("-screenDiagonal".equalsIgnoreCase(key)) {
				int value = Util.toInt(arguments.get(key));
				if (configuration.calibration != null) {
					configuration.calibration.setScreenDiagonal_mm(value);
				}
			}
		}
	}

	private static LinkedHashMap<String, String> buildArgumentsHashMap(String[] args) {
		LinkedHashMap<String, String> arguments = new LinkedHashMap<String, String>();
		String temporaryArgument = null;
		// if ( args.length < 2 ) {
		// usage(null);
		// }

		for (String argument : args) {
			if (argument.equals("--help") || argument.equals("-h")) {
				usage(null);
			}

			if (argument.startsWith("-") && temporaryArgument == null) {
				temporaryArgument = argument;
			} else {
				if (temporaryArgument != null) {
					arguments.put(temporaryArgument, argument);
					temporaryArgument = null;
				} else {
					usage(temporaryArgument + " " + argument);
				}
			}
		}
		return arguments;
	}

	private static void usage(String argument) {

		System.out.println("Usage: java -jar " + Consts.APP_NAME + ".jar ");
		System.out.println("           -task circular : task to display (circular|linear)");
		System.out.println("           -cornerX : topleft corner of circles, from toplef of window (pixel)");
		System.out.println("           -cornerY : topleft corner of circles, from toplef of window (pixel)");
		System.out.println("           -centerX : center of circles !supersedes cornerX! (pixel) ");
		System.out.println("           -centerY : center of circles !supersedes cornerY! (pixel)");
		System.out.println("           -externalRadius : radius of external circle (pixel)");
		System.out.println("           -internalRadius : radius of internal circle (pixel)");
		System.out.println(
				"           -indexOfDifficulty : index of difficulty !supersedes internalRadius! (google: steering law) ");
		System.out.println("           -borderRadius 1: width of the border of both circles (pixel) ");
		System.out.println("           -cursorRadius 16 : radius of circle cursor (pixel)");
		System.out.println(
				"           -borderColor white : color of both circles (see: https://docs.oracle.com/javase/6/docs/api/java/awt/Color.html) ");
		System.out.println("           -backgroundColor black  ");
		System.out.println("           -cursorColorRecord red : name of cursor color when recording ");
		System.out.println("           -cursorColorWait yellow : name of cursor color when waiting");
		System.out.println(
				"           -autoStart 3600 : delay before auto start recording, press space to start earlier (second)");
		System.out.println("           -cycleMaxNumber 6 : Record+Pause cycles to run (number)");
		System.out.println("           -cycleDuration 20: duration of one Record/Pause period (seconds)");
		// System.out.println(" -tabletSize_mm 311x216: width and height of graphic
		// tablet (mm) ");
		// System.out.println(" -tabletSize_px 62200x43200: width and heigh of graphic
		// tablet (pixel)");
		System.out.println("           -tabletSize 311x216=62200x43200: width and heigh of graphic tablet (mm=pixel)");
		System.out.println("           -screenDiagonal 400: diagonal of the screen (mm)");

		if (argument != null) {
			System.out.println("This argument is not clear : " + argument);
		}

		System.exit(0);
	}

	/**
	 * Display the main window of the application to the user.
	 */
	private static void showMainWindow(Configuration configuration) {
		logger.info("Showing the main window.");
		MainWindow mainWindow = MainWindow.getInstance(configuration);
		mainWindow.buildAndShow();
	}

	private static void logBasicSystemInfo() {
		logger.setLevel(java.util.logging.Level.WARNING);
		logger.info("Launching the application...");
		logger.config("Operating System: " + System.getProperty("os.name") + " " + System.getProperty("os.version"));
		logger.config("JRE: " + System.getProperty("java.version"));
		logger.info("Java Launched From: " + System.getProperty("java.home"));
		logger.config("Class Path: " + System.getProperty("java.class.path"));
		logger.config("Library Path: " + System.getProperty("java.library.path"));
		logger.config("Application Name: " + Consts.APP_NAME + " " + Consts.APP_VERSION);
		logger.config("User Home Directory: " + System.getProperty("user.home"));
		logger.config("User Working Directory: " + System.getProperty("user.dir"));
		logger.info("Test INFO logging.");
		logger.fine("Test FINE logging.");
		logger.finest("Test FINEST logging.");
	}
}
