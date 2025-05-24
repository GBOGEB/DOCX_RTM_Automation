def main():
	# Create new directory structure
	create_directory_structure()

	# Copy files to new locations
	move_files()

	# Update paths in configuration
	update_paths_config()

	# Update Python imports
	update_script_imports()

	# Update run_pipeline.py
	update_run_pipeline()

	# Create README
	create_readme()

	# Update README with test info
	update_readme_with_tests()

	# Create project runner
	create_project_runner()

	# Create test runner
	create_test_runner()

	# Create requirements file
	create_requirements_file()

	# Define test section content
	test_section = "\n## Tests\nRun automated tests with: python run_tests.py"

	# Append test section to content
	content = content + test_section

	print("\n" + "="*50)
	print("Refactoring completed successfully!")
	print("="*50)
	print("\nTo start using the refactored repository:")
	print("1. Review the README.md file")
	print("2. Run the pipeline with: python run.py")
	print("3. Run tests with: python run_tests.py") 
	print("4. Check the new directory structure for correctness")

	return 0

if __name__ == "__main__":
	main()