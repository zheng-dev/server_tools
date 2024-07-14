
import turtle
import time

def main():
    print("one=%d,%s,%s,%d" % (1,"3","abdc",b(30)))
    #taiyanhua()
    five_star()


def taiyanhua():
    #"""sun flower"""
    turtle.color("red","yellow")
    turtle.begin_fill()
    for _ in range(50):
        turtle.forward(200)
        turtle.left(170)
        turtle.end_fill()
    turtle.mainloop()

def five_star():
    """five star
    """
    turtle.pensize(5)
    turtle.color("red","blue")
    turtle.begin_fill()
    for _ in range(5):
        turtle.forward(200)
        turtle.right(144)
    
    turtle.penup()
    turtle.goto(-100,-120)    
    turtle.pendown()
    turtle.circle(110)

    turtle.end_fill()
    time.sleep(2)

    turtle.penup()
    turtle.goto(-150,-120)
    turtle.color("violet")
   
    turtle.write("Done",font=("Arial",40,'normal'))
    turtle.mainloop()

def b(b:int):
    """test return
    """
    return 3+b
main()  