from drafter import *
from dataclasses import dataclass
import math

set_website_title("BudgetCad")
set_site_information(
    author="Alexander Carpenter",
    description="Make Simple Designs and Assemblies",
    links=["https://github.com/your-username/your-repository"]
)
hide_debug_information()
set_website_framed(False)


#defining dataclasses
@dataclass
class State:
    chosen_shape: str
    designs: list[Design]
    pending_volume: float
    materials: list[Material]
    assemblies: list[Assembly]
    pending_assembly: list[Design]
    pending_assembly_name: str
    
@dataclass
class Material:
    name: str
    cost: float
    density: float

@dataclass
class Design:
    name: str
    volume: float
    
@dataclass
class Assembly:
    name: str
    designs: list[Design]
    
    

#defining routes

@route
def index(state: State) -> Page:
    #later add if statement so that when a design is created it shows the option to show the design table
    return Page(state, ["Home Page!!!\n", Button("Make a Design!", "designer"), Button("Build an Assembly!", "assembly_builder")])

@route
def designer(state: State, selected_shape: str = "Sphere") -> Page:
    state.chosen_shape = selected_shape
    
    complete_page = ["Pick a shape:\n",
                        SelectBox("selected_shape", ["Rectangular Prism", "Sphere"], state.chosen_shape),
                        "\n",
                        Button("Choose Shape", "designer"),
                        "\nCurrent Shape: " + selected_shape]
    
    if state.chosen_shape == "Sphere":
        complete_page.append(TextBox("dim1"))
    if state.chosen_shape == "Rectangular Prism":
        complete_page.append(TextBox("dim1"))
        complete_page.append(TextBox("dim2"))
        complete_page.append(TextBox("dim3"))
    
    complete_page.append(Button("Calculate Volume!", "calculate_volume"))
    
    return Page(state, complete_page)

@route
def error_page(state: State):
    return Page(state, ["Something went wrong! Check to make sure your inputs are correctly formatted. Inputs should be in decimal only. Eg: 12345 or 1.2345. Fractions and operators are not accepted.\n", Button("Return Home!", "index")])
@route
def calculate_volume(state: State, dim1: str = "", dim2: str = "", dim3: str = "",):
    """
    if not is_acceptable_input(dim2):
        return error_page(state)
    if not is_acceptable_input(dim3):
        return error_page(state)
    """
    complete_page= ["Your shape was: " + state.chosen_shape,
                    "\n",
                    ]
    
    if state.chosen_shape == "Sphere":
        if not is_acceptable_input(dim1):
            return error_page(state)
        radius_float = float(dim1)
        state.pending_volume = (4/3)*math.pi*(radius_float**3)
        complete_page.append("Radius: " + dim1 + "\nVolume:" + str(state.pending_volume))
    
    if state.chosen_shape == "Rectangular Prism":
        if not is_acceptable_input(dim1):
            return error_page(state)
        if not is_acceptable_input(dim2):
            return error_page(state)
        if not is_acceptable_input(dim3):
            return error_page(state)
        
        length_float = float(dim1)
        width_float = float(dim2)
        height_float = float(dim3)
        complete_page.append("Length: " + dim1)
        complete_page.append("\nWidth: " + dim2)
        complete_page.append("\nHeight: " + dim3)
        state.pending_volume = length_float * width_float * height_float
        complete_page.append("\nVolume: " + str(state.pending_volume))

    complete_page.append("Name your design:\n")
    complete_page.append(TextBox("design_name"))
    complete_page.append(Button("Save Design?", "save_design"))
    
    
    return Page(state, complete_page)

  
@route
def save_design(state: State, design_name: str):
    design_name = is_acceptable_name(design_name, state.designs)
    state.designs.append(Design(design_name, state.pending_volume))
    return Page(state, ["Design saved as " + design_name +"\n", Button("Return Home", "index"), "\n", Button("View Designs", "view_designs")])
    
@route
def view_designs(state: State):
    return Page(state, [Header("Designs"), Table(state.designs,["Name", "Volume"]), "\n", Button("Return Home", "index")])

@route
def assembly_builder(state: State):
    design_names = []

    for design in state.designs:
        design_names.append(design.name)

    if len(design_names) == 0:
        return Page(state, ["No designs found", Button("Return Home", "index")])

    complete_page = [Header("Assembly Builder")]

    if state.pending_assembly_name == "":
        complete_page.append("Assembly Name:")
        complete_page.append(TextBox("assembly_name"))
    else:
        complete_page.append("Assembly: " + state.pending_assembly_name)

    complete_page.append("Current Assembly:")

    for design in state.pending_assembly:
        complete_page.append(design.name)

    complete_page.append("Choose a Design:")
    complete_page.append(SelectBox("selected_design", design_names, design_names[0]))
    complete_page.append("Quantity:")
    complete_page.append(TextBox("quantity"))
    complete_page.append(Button("Add to assembly", "add_to_assembly"))
    complete_page.append(Button("Return Home!!!", "index"))

    return Page(state, complete_page)


@route
def add_to_assembly(state: State, assembly_name: str = "", selected_design: str = "", quantity: str = ""):
    if not quantity.isdigit() or int(quantity) < 1:
        return Page(state, ["Please enter a valid quantity", Button("Back to assembly builder", "assembly_builder")])

    if assembly_name != "":
        state.pending_assembly_name = assembly_name

    if state.pending_assembly_name == "":
        return Page(state, ["Enter an assembly name!", Button("Back to assembly builder", "assembly_builder")])

    chosen_design = None

    for design in state.designs:
        if design.name == selected_design:
            chosen_design = design

    if chosen_design == None:
        return Page(state, ["Design not found!", Button("Try Again", "assembly_builder")])

    for i in range(int(quantity)):
        state.pending_assembly.append(chosen_design)

    return Page(state, [
        Header("Current Asembly"),
        *[design.name for design in state.pending_assembly],
        Button("Add another Design", "assembly_builder"),
        Button("Finish assembly", "finish_assembly")
    ])

@route
def finish_assembly(state: State):
    new_assembly = Assembly(
        state.pending_assembly_name,
        state.pending_assembly.copy()
    )

    state.assemblies.append(new_assembly)

    state.pending_assembly = []
    state.pending_assembly_name = ""

    return Page(state, [
        Header("Assembly Saved!"),
        "Assembly: " + new_assembly.name,
        Button("Return Home", "index")
    ])




#defining functions

def is_acceptable_input(number: str) -> bool:
    testfor = "XXX"
    testing = True
    test = ""
    if number == "":
        return False
    if not ("." in number):
        return number.isdigit()
    else:
        testfor = number
        for i in range(len(testfor)):
            if testing:
                if testfor[i] == ".":
                    testing = False
                else:
                    test = test + testfor[i]
            else:
                test = test + testfor[i]
        return test.isdigit()
        
            
def is_acceptable_name(name: str, list_of_designs: list[Design]) -> str:
    names = []
    if name == "":
        name = "Untitled"
    for i in range(len(list_of_designs)):
        names.append(list_of_designs[i].name)
    
    if not (name in names):
        return name
    else:
        i = 1
        searching = True
        while searching:
            if not (name + " ("+str(i)+")") in names:
                searching = False
            else:
                i = i + 1
        return name + " (" + str(i) + ")"
            
        



start_server(State("Sphere", [], [], 0.0, [], [], ""))    
    

