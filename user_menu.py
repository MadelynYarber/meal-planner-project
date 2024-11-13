#To gather user information

#Ask for meal/diet preferences, give menu option: 
# Regular, Vegetarian, Vegan, Pescatarian, etc?

# What are your goals?

#Possible way to do it:
diet = input("What is your diet preference? ")
# calories as string, int, float, etc?
calories = input("What do you want your daily calorie intake to be? ")
# do the same for protein and/or carbs? or would that be too much trouble?

print("Your diet preference is: ", diet)
print("Your ideal daily calorie intake is: ", calories)

#or more detailed way ~~~~~~~~~~~~~~

print("Which of these best fits your dietary preference:")
print("Regular, Vegetarian, Pescetarian, or Vegan")
diet = input()

#need to do a loop or validation check for it there is wrong input
if diet == "Regular" or diet == "regular":
    print("Your dietary preference is regular")
if diet == "Vegetarian" or diet == "vegetarian":
    print("Your dietary preference is vegetarian")
if diet == "Pescetarian" or diet == "pescetarian":
    print("Your dietary preference is pescetarian")
if diet == "Vegan" or diet == "vegan":
    print("Your dietary preference is vegan")




calories = int(input("What do you want your daily calorie intake to be? "))
if calories < 1000:
    print("It is recommended to intake at least 1,200 calories a day")
    choice = input("Do you wish to continue with this amount of calories: y or n")
    if choice == "y":
        print("you chosen calorie intake is: ", calories)
    elif choice == "n":
        calories = int(input("What do you want your daily calorie intake to be? "))

print("Your chosen daily calorie intake is ", calories)