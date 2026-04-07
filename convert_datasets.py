from proj.processing.convert_fafb import main as convert_fafb
from proj.processing.convert_mcns import main as convert_mcns
from proj.processing.convert_manc import main as convert_manc

def main():
    print("Converting FAFB...")
    convert_fafb()
    print("\nConverting MCNS...")
    convert_mcns()
    print("\nConverting MANC...")
    convert_manc()
 
if __name__ == "__main__":
    main()