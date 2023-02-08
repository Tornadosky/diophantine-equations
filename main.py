from parser_1 import *

if __name__ == "__main__":
    # return dict for z3 solution
    def return_sol(s):
        if s.check() == sat:
            model = s.model()
            dict = {}
            for d in model:
                dict[str(d)] = model[d]
            return dict
        else:
            return "No solution!"
    
    def solve(filename):
        """
        :type filename: str
        :rtype: Dict[str, int]
        """
        with open(filename, 'r') as file:
            s = Solver()

            # read from file and replace new lines
            data = file.read().replace('\n', ' ')
            
            # parse input, return List[List, List]
            expr = result(ParseSys().parse(data))

            # go through list of equasions and list of constraints
            # and add them to z3 solver
            for elem in expr:
                for item in elem:
                    z3_expr = item.toZ3()
                    s.add(z3_expr)

            return return_sol(s)
    
    res = solve("test_files/simple.txt")
    print("One solution is: ", res)