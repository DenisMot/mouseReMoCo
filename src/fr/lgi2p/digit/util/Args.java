package fr.lgi2p.digit.util;

import java.util.regex.*;

public final class Args {

	private Args() {

	}

	public static void checkForContent(String aText) {
		if (!Util.textHasContent(aText)) {
			throw new IllegalArgumentException("Text has no visible content");
		}
	}

	public static void checkForRange(int aNumber, int aLow, int aHigh) {
		if (!Util.isInRange(aNumber, aLow, aHigh)) {
			throw new IllegalArgumentException(aNumber + " not in range " + aLow + ".." + aHigh);
		}
	}

	public static void checkForPositive(int aNumber) {
		if (aNumber < 1) {
			throw new IllegalArgumentException(aNumber + " is less than 1");
		}
	}

	public static void checkForMatch(Pattern aPattern, String aText) {
		if (!Util.matches(aPattern, aText)) {
			throw new IllegalArgumentException(
					"Text " + Util.quote(aText) + " does not match '" + aPattern.pattern() + "'");
		}
	}

	public static void checkForNull(Object aObject) {
		if (aObject == null) {
			throw new NullPointerException();
		}
	}
	
	public static void checkForColor(String color) {
		if(Util.toColor(color) == null ) {
			throw new IllegalArgumentException( color + " is not a color see https://docs.oracle.com/javase/6/docs/api/java/awt/Color.html ");
		}
	}

}
