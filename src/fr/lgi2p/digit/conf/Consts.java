package fr.lgi2p.digit.conf;

public final class Consts {

	public static final String APP_NAME = "mouseReMoCo";

	public static final String APP_VERSION = "1.2.5";

	public static final double INCH_PER_MM = 25.4;
	
	public static final String DATE_FORMAT = "yyyy-MM-dd";


	public static final boolean PASSES = true;

	public static final boolean FAILS = false;


	public static final boolean SUCCESS = true;

	public static final boolean FAILURE = false;


	public static final int NOT_FOUND = -1;


	public static final String NEW_LINE = System.getProperty("line.separator");

	public static final String FILE_SEPARATOR = System.getProperty("file.separator");

	public static final String PATH_SEPARATOR = System.getProperty("path.separator");

	public static final String EMPTY_STRING = "";
	public static final String SPACE = " ";
	public static final String TAB = "\t";
	public static final String SINGLE_QUOTE = "'";
	public static final String PERIOD = ".";
	public static final String DOUBLE_QUOTE = "\"";
	public static final String ELLIPSIS = "...";
	public static final String BACK_SLASH = "\\";


	private Consts() {
		throw new AssertionError();
	}
}