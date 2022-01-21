package fr.lgi2p.digit.exception;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import fr.lgi2p.digit.util.Args;

public final class InvalidInputException extends Exception {
	
	 /**
	 * 
	 */
	private static final long serialVersionUID = -948693628832900970L;
	private List<String> fErrorMessages = new ArrayList<String>();
	  
	  /**  Add a new error message to this exception. */
	  public void add(String aErrorMessage){
	    Args.checkForContent(aErrorMessage);
	    fErrorMessages.add(aErrorMessage);
	  }
	  
	  /** Return an unmodfiable list of error messages. */
	  public List<String> getErrorMessages(){
	    return Collections.unmodifiableList(fErrorMessages);
	  }

	  /** Return <tt>true</tt> only if {@link #add(String)} has been called at least once.*/
	  public boolean hasErrors(){
	    return ! fErrorMessages.isEmpty();
	  }

	 
	 
	}
	 
