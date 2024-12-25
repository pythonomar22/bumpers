def test_imports():
    print("\nTesting imports...")
    
    from bumpers.core.engine import CoreValidationEngine
    print("✓ Successfully imported CoreValidationEngine")
    
    from bumpers.validators.content import ContentFilterValidator
    print("✓ Successfully imported ContentFilterValidator")
    
    assert CoreValidationEngine
    assert ContentFilterValidator
    print("✓ All imports successful!")

if __name__ == "__main__":
    test_imports() 