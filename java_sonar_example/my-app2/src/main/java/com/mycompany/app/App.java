package com.mycompany.app;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Hello world!
 *
 */
public class App 
{
public void doSomething(String str) {
  if (Math.abs(str.hashCode()) > 0) { // Noncompliant
    // ...
  }
}


    public static void main( String[] args )
    {


        System.out.println( "Hello World!" );
    }
}
