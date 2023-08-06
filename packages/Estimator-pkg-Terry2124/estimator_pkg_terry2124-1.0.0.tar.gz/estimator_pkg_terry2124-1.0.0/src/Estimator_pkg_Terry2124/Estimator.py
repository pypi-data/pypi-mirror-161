#Construction materials estimator
#Cubic Feet to Cubic Yard
#Option 1
from math import pi
def cubic_feet_yard():
    cfy_length = int(input("Enter length in feet "))
    cfy_width = int(input ("Enter width in feet "))
    cfy_depth = int(input ("Enter depth in inches "))
    cfy_result = cfy_length * cfy_width * (cfy_depth/12) / 27
    print(f"Cubic feet to cubic yard {cfy_result}")
    print(f"Let's round that up {cfy_result.__round__(None)}")
    print("_____________________________")
    print("_____________________________")
    main()
    return
#Area Calculator Rectangle
#Option 2
def area_calculation():
    ac_length = int(input("Enter length "))
    ac_width = int(input("Enter width "))
    ac_result = ac_length * ac_width
    print("AREA calculation of a RECTANGLE")
    print(f"Result: {ac_result}")
    print("_____________________________")
    print("_____________________________")
    main()
    return
#Area of a triangle
#Option 3
def area_triangle():
    import math
    a_tri_1 = int(input("Enter side 1(a) "))
    a_tri_2 = int(input("Enter side 2(b) "))
    a_tri_3 = int(input("Enter side 3(c) "))
    a_tri_result = (a_tri_1 + a_tri_2 + a_tri_3) / 2
    a_tri_result_2 = math.sqrt(a_tri_result * (a_tri_result - a_tri_1) * (a_tri_result - a_tri_2) * (a_tri_result - a_tri_3))
    print(f"The area result of the triangle : {a_tri_result_2} square feet")
    print("_____________________________")
    print("_____________________________")
    main()
    return
#Area of a trapezoid
#Option 4
def area_trapezoid():
    import math
    a_trap_1 = int(input("Enter base (b1) "))
    a_trap_2 = int(input("Enter base (b2) "))
    a_trap_3 = int(input("Enter height (h) "))
    a_trap_result = (a_trap_1 + a_trap_2) / 2 * a_trap_3
    print(f"The area of the trapezoid : {a_trap_result} square feet")
    print("_____________________________")
    print("_____________________________")
    main()
    return
#Area of a circle
#Option 5
def area_circle():
    import math
    a_circle = int(input("Enter radius of circle (r) "))
    a_circle_result = pi * a_circle ** 2
    print(f"The area of the circle : {a_circle_result} square feet")
    print("_____________________________")
    print("_____________________________")
    main()
#Area of a sector
#Option 6
def area_sector():
    import math
    sec_radius = int(input("Enter radius (r) "))
    sec_angle = int(input("Enter angle (A) "))
    a_sec_result = (sec_angle / 360) * pi * sec_radius ** 2
    print(f"The area of the sector : {a_sec_result} square feet")
    print("_____________________________")
    print("_____________________________")
    main()
#Area of an ellipse
#Option 7
def area_ellipse():
    import math
    semi_major = int(input("Enter semi-major (a) "))
    semi_minor = int(input("Enter semi-minor (b) "))
    ellipse_result = pi * semi_major * semi_minor
    print(f"The area of the ellipse : {ellipse_result} square feet")
    print("_____________________________")
    print("_____________________________")
    main()
#Area of a parallelogram
#Option 8
def area_parallelogram():
    a_base = int(input("Enter base (b) "))
    a_height = int(input("Enter height (h) "))
    parallelogram_result = a_base * a_height
    print(f"The area of the parallelogram : {parallelogram_result} square feet")
    print("_____________________________")
    print("_____________________________")
    main()
#Concrete slab
#Option 9
def con_slab():
    con_thickness = int(input("Enter thickness in inches "))
    con_width = int(input("Enter width in feet "))
    con_length = int(input("Enter length in feet "))
    con_slab_result = (con_thickness / 12) * con_width * con_length / 35.315
    print(f"The amount of concrete required : {con_slab_result} cubic metres")
    print("Volume in Cubic Meters (m3) = Volume in Cubic Feet (ft3) x 0.0283")
    print("_____________________________")
    print("_____________________________")
    main()
#Main program input
def main():
    option_list = [
        "Exit Program : (0)",
        "Cubic feet to cubic yard : (1)",
        "Area of a rectangle : (2)",
        "Area of a triangle : (3)",
        "Area of a trapezoid : (4)",
        "Area of a circle : (5)",
        "Area of a sector : (6)",
        "Area of a ellipse : (7)",
        "Area of a parallelogram (8)",
        "Concrete slab in m3 : (9)"
    ]
    print("Welcome to construction estimator")
    print(" ")
    print(" ")
    print(" ")
    print("-----------------------------")
    print("*****  Enter an option  ***** ")
    print("-----------------------------")

    for i in option_list:
        print(i)
    input_option = int(input("Please enter your option "))
    print(" ")
    print(" ")  
    if input_option == 1:
        cubic_feet_yard()
    elif input_option == 2:
        area_calculation()
    elif input_option == 3:
        area_triangle()
    elif input_option == 0:
        exit()
    elif input_option == 4:
        area_trapezoid()
    elif input_option == 5:
        area_circle()
    elif input_option == 6:
        area_sector()
    elif input_option == 7:
        area_ellipse()
    elif input_option == 8:
        area_parallelogram()
    elif input_option == 9:
        con_slab()
    else:
        print("You have made an incorrect selection, please try again")
        main()
main()
