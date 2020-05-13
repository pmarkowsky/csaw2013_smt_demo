"""
Crackme solution using z3.
"""
import binascii
import z3

encoded_str = binascii.unhexlify("872b735a30205f5f27391e732e645d72296876671923423c1e5c3d6d487837375b374732523a76696564202d54483d39602e52343b6a71298d2d5a6d472b416d4a38246d296672075e6b205d57241b45687160553755706e3a4c4f6435293349736a5d5f37375b1d6f576035611923443139333b5c706a5c60343b5e14366068766065312b23246436592b252377652e597e4c256a33436a765a62645410695b232b7d6f1b84723828461728597e5b3b6e2a414b2e5609466149736758674773583c4d23442738196b772b7359382a656550708d1f34510d5e6b5a7339282a40497350240933714e222f696425316c62")

lookup_table_str = "We go about our daily lives understanding almost nothing of the world. Few of us spend much time wondering why nature is the way it is; where the cosmos came from;... why we remember the past and not the future; and why there is a universe."


def MakeInputStr(solver_str_model):
    output_str = ""
    entries = []

    max_index = 0

    for i in xrange(0, solver_str_model.num_entries()):
        entries.append([ x.as_long() for x in solver_str_model.entry(i).as_list()])

    # sort by index
    entries = sorted(entries, key=lambda x: x[0])
    return "".join(map(lambda x: chr(x[1]), entries))[0:32]


def FindStartingPoint(user_input_array):
    index = z3.BitVec('dl', 8)
    
    for i in xrange(32):
        index += user_input_array[i]
    return index


def CreateLookupTable(solver, lookup_table_str):
    lookup_table = z3.Array("lookup_table", z3.BitVecSort(8), z3.BitVecSort(8))
    
    for i in xrange(len(lookup_table_str)):
        solver.add(lookup_table[i] == ord(lookup_table_str[i]))
        
    return solver, lookup_table

def Main():
    solver = z3.Solver()
    user_input_array = z3.Array("input", z3.BitVecSort(8), z3.BitVecSort(8))
    output_str = z3.Array("output_str", z3.BitVecSort(8), z3.BitVecSort(8))
    solver, lookup_table = CreateLookupTable(solver, lookup_table_str)
    
    # add the path conditions that the user_str_index is equal to the sum of the
    # first 32 characters
    user_str_idx = FindStartingPoint(user_input_array)
    # make sure the user_str_idx stays modulo 32
    user_str_idx = user_str_idx % 0x20
    
    # create conditions from the encoding loop
    for i in xrange(240):
        output_str = z3.Store(output_str, i, 
                (user_input_array[user_str_idx] ^ lookup_table[i]) + user_str_idx) 
        user_str_idx = (output_str[i] + user_str_idx) % 0x20
    
    # limit input to the printable ascii range
    for i in xrange(0x20):
        solver.add(z3.And(z3.UGE(user_input_array[i], 32), 
                          z3.ULT(user_input_array[i], 127)))
        
    # Make sure our output_string is constrained to match our expected result
    for i in xrange(len(encoded_str)):
        solver.add(output_str[i] == ord(encoded_str[i]))
        
    if solver.check() == z3.sat:
        m = solver.model()
        print 'Valid Serial is: ' + MakeInputStr(m[user_input_array])
    else:
        # this is unsat and we can't find a solution
        print 'No solution found'
               

if __name__ == '__main__':
    Main()
