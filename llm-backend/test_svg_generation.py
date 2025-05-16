"""Test SVG Generation Functionality"""
from service.graph_builder import generate_architecture_svg, create_default_svg, create_error_svg

def test_svg_generation():
    """Test if the SVG generation function works correctly"""
    # Test error SVG
    error_svg = create_error_svg("https://github.com/test/repo", "Test error message")
    print(f"Error SVG length: {len(error_svg)}")
    print(f"Error SVG preview: {error_svg[:100]}...")
    
    # Test default SVG
    components = {
        "frontend": {"files": ["index.html", "style.css"]},
        "backend": {"files": ["app.py", "models.py"]},
    }
    default_svg = create_default_svg("https://github.com/test/repo", components)
    print(f"Default SVG length: {len(default_svg)}")
    print(f"Default SVG preview: {default_svg[:100]}...")
    
    # Test generating SVG with simple structure
    simple_structure = """
    README.md
    src/
        main.py
        utils.py
    tests/
        test_main.py
    """
    generated_svg = generate_architecture_svg("https://github.com/test/repo", simple_structure)
    print(f"Generated SVG length: {len(generated_svg)}")
    print(f"Generated SVG preview: {generated_svg[:100]}...")
    
    # Save SVGs to files for viewing
    with open("test_error_svg.svg", "w") as f:
        f.write(error_svg)
    
    with open("test_default_svg.svg", "w") as f:
        f.write(default_svg)
        
    with open("test_generated_svg.svg", "w") as f:
        f.write(generated_svg)
    
    print("Test completed, SVG files have been saved")

if __name__ == "__main__":
    test_svg_generation() 