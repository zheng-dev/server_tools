package com.app;

import bsh.Interpreter;

public class MyShit
{
	static
	{
		System.out.println("this is in static blog");
	}

	public int id;
	
	public static void main(String[] args)
	{		
		try
		{
			Interpreter i = new Interpreter();
			i.source("helloWorld.bsh");
		}
		catch(Exception e)
		{
			e.getMessage();
		}
		System.out.println("this is in main method : hello shit");
	}
	public MyShit(int id){
		this.id=id;
	}
	
	public static void shit()
	{
		System.out.println("hello shit!!!");
	}

	public void haha()
	{
		System.out.printf("this is static method haha,-id=%d\n",this.id);
	}
}
