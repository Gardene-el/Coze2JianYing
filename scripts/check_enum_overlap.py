
try:
    from pyJianYingDraft import IntroType, OutroType
    
    intro_members = set(name for name, value in vars(IntroType).items() if not name.startswith("__"))
    outro_members = set(name for name, value in vars(OutroType).items() if not name.startswith("__"))
    
    intersection = intro_members.intersection(outro_members)
    
    print(f"IntroType members count: {len(intro_members)}")
    print(f"OutroType members count: {len(outro_members)}")
    
    if intersection:
        print(f"Found {len(intersection)} overlapping members:")
        for name in intersection:
            print(f" - {name}")
    else:
        print("No overlapping members found.")
        
except ImportError:
    print("pyJianYingDraft not installed or cannot import types.")
except Exception as e:
    print(f"An error occurred: {e}")
