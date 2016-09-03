package testBean;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Date;
import java.util.Scanner;

import bsh.EvalError;
import bsh.Interpreter;

import com.app.MyShit;

public class Main {
	public enum ColorEnum{
		red,green,yellow,blue;
	}
	public static void main(String[] args) throws IOException {
		Interpreter i=new Interpreter();
		Scanner input=new Scanner(System.in);
		Main m=new Main();
		for(int ii=0;ii<4;ii++){
			m.test(i);
			System.out.printf("get %d\n",input.nextInt());
		}
		ColorEnum color1=ColorEnum.blue;
		input.close();
		System.out.printf("test:%d\r",color1.ordinal());
	}
	
	protected void test(Interpreter i){
		try{
			i.set("date",new Date());
			
			i.source("helloWorld.bsh");
			MyShit shit=(MyShit)i.get("shit");
			shit.id-=5;
			shit.haha();
		}catch(FileNotFoundException FFE){
			System.out.println("test1");
		}
		catch(IOException FFE){
			System.out.println("test2");
		}
		catch(EvalError FFE){
			System.out.println(FFE.getMessage());
		}
	}

}

