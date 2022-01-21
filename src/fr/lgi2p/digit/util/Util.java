package fr.lgi2p.digit.util;

import java.util.*;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.awt.Color;
import java.lang.reflect.Field;
import java.math.BigDecimal;

import fr.lgi2p.digit.conf.Consts;
import fr.lgi2p.digit.exception.InvalidInputException;

import java.text.SimpleDateFormat;
import java.text.DateFormat;
import java.text.ParseException;

/**
 * Static convenience methods for common tasks, which eliminate code
 * duplication.
 */
public final class Util {



	public static boolean textHasContent(String aText) {
		return (aText != null) && (aText.trim().length() > 0);
	}

	static public boolean isInRange(int aNumber, int aLow, int aHigh) {
		if (aLow > aHigh) {
			throw new IllegalArgumentException("Low is greater than High.");
		}
		return (aLow <= aNumber && aNumber <= aHigh);
	}

	public static Boolean parseBoolean(String aBoolean) {
		if (aBoolean.equalsIgnoreCase("true")) {
			return Boolean.TRUE;
		} else if (aBoolean.equalsIgnoreCase("false")) {
			return Boolean.FALSE;
		} else {
			throw new IllegalArgumentException("Cannot parse into Boolean: " + aBoolean);
		}
	}
	
	
	static public int toInt(String number) {
		return Integer.parseInt(number);
	}
	
	static public Color toColor(String color) {
		Color returnColor;
		try {
		    Field field = Class.forName("java.awt.Color").getField(color);
		    returnColor = (Color)field.get(null);
		} catch (Exception e) {
			returnColor = null;
		}
		return returnColor;
	}

	public static Logger getLogger(Class<?> aClass) {
		return Logger.getLogger(aClass.getPackage().getName());
	}

	public static Date parseDate(String aDate, String aName) throws InvalidInputException {
		Date result = null;
		if (textHasContent(aDate)) {
			DateFormat FORMAT = new SimpleDateFormat(Consts.DATE_FORMAT);
			FORMAT.setLenient(false);
			try {
				result = FORMAT.parse(aDate);
			} catch (ParseException ex) {
				throwEx(aName + " is not a valid date: " + aDate);
			}
		}
		return result;
	}

	public static String format(Object aObject) {
		String result = "";
		if (aObject != null) {
			if (aObject instanceof Date) {
				Date date = (Date) aObject;
				DateFormat FORMAT = new SimpleDateFormat(Consts.DATE_FORMAT);
				FORMAT.setLenient(false);
				result = FORMAT.format(date);
			} else {
				result = String.valueOf(aObject);
			}
		}
		return result;
	}

	public static BigDecimal parseBigDecimal(String aBigDecimal, String aName) throws InvalidInputException {
		BigDecimal result = null;
		if (textHasContent(aBigDecimal)) {
			try {
				result = new BigDecimal(aBigDecimal);
			} catch (NumberFormatException exception) {
				throwEx(aName + " is not a valid number.");
			}
		}
		return result;
	}

	private static void throwEx(String aMessage) throws InvalidInputException {
		InvalidInputException ex = new InvalidInputException();
		ex.add(aMessage);
		throw ex;
	}

	public static boolean matches(Pattern aPattern, String aText) {
		Matcher matcher = aPattern.matcher(aText);
		return matcher.matches();

	}

	public static String quote(String aText) {
		return java.util.regex.Pattern.quote(aText);
	}
}