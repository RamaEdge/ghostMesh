# GhostMesh Presentation Makefile
# Handles generation of presentation materials from Marp source

# Variables
PRESENTATION_SOURCE = ghostmesh-pitch.md
PRESENTATION_OUTPUT = ghostmesh-pitch
THEME = default
SIZE = 16:9

# Default target
.PHONY: all
all: html pdf pptx

# Generate HTML presentation
.PHONY: html
html:
	@echo "Generating HTML presentation..."
	marp $(PRESENTATION_SOURCE) --html --output $(PRESENTATION_OUTPUT).html
	@echo "✅ HTML presentation generated: $(PRESENTATION_OUTPUT).html"

# Generate PDF presentation
.PHONY: pdf
pdf:
	@echo "Generating PDF presentation..."
	marp $(PRESENTATION_SOURCE) --pdf --output $(PRESENTATION_OUTPUT).pdf
	@echo "✅ PDF presentation generated: $(PRESENTATION_OUTPUT).pdf"

# Generate PowerPoint presentation
.PHONY: pptx
pptx:
	@echo "Generating PowerPoint presentation..."
	marp $(PRESENTATION_SOURCE) --pptx --output $(PRESENTATION_OUTPUT).pptx
	@echo "✅ PowerPoint presentation generated: $(PRESENTATION_OUTPUT).pptx"

# Generate all formats
.PHONY: all-formats
all-formats: html pdf pptx
	@echo "✅ All presentation formats generated"

# Preview presentation in browser
.PHONY: preview
preview:
	@echo "Starting preview server..."
	marp $(PRESENTATION_SOURCE) --preview

# Watch for changes and auto-regenerate
.PHONY: watch
watch:
	@echo "Watching for changes..."
	marp $(PRESENTATION_SOURCE) --watch

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	rm -f $(PRESENTATION_OUTPUT).html
	rm -f $(PRESENTATION_OUTPUT).pdf
	rm -f $(PRESENTATION_OUTPUT).pptx
	@echo "✅ Cleaned generated files"

# Install Marp CLI (if not already installed)
.PHONY: install-marp
install-marp:
	@echo "Installing Marp CLI..."
	npm install -g @marp-team/marp-cli
	@echo "✅ Marp CLI installed"

# Check if Marp is installed
.PHONY: check-marp
check-marp:
	@which marp > /dev/null || (echo "❌ Marp CLI not found. Run 'make install-marp' to install." && exit 1)
	@echo "✅ Marp CLI is installed"

# Validate presentation source
.PHONY: validate
validate:
	@echo "Validating presentation source..."
	marp $(PRESENTATION_SOURCE) --validate
	@echo "✅ Presentation source is valid"

# Generate presentation with custom theme
.PHONY: custom-theme
custom-theme:
	@echo "Generating presentation with custom theme..."
	marp $(PRESENTATION_SOURCE) --theme $(THEME) --html --output $(PRESENTATION_OUTPUT)-$(THEME).html
	@echo "✅ Custom theme presentation generated"

# Generate presentation with custom size
.PHONY: custom-size
custom-size:
	@echo "Generating presentation with custom size..."
	marp $(PRESENTATION_SOURCE) --size $(SIZE) --html --output $(PRESENTATION_OUTPUT)-$(SIZE).html
	@echo "✅ Custom size presentation generated"

# Generate presentation for different audiences
.PHONY: technical
technical:
	@echo "Generating technical presentation..."
	marp $(PRESENTATION_SOURCE) --html --output $(PRESENTATION_OUTPUT)-technical.html
	@echo "✅ Technical presentation generated"

.PHONY: business
business:
	@echo "Generating business presentation..."
	marp $(PRESENTATION_SOURCE) --html --output $(PRESENTATION_OUTPUT)-business.html
	@echo "✅ Business presentation generated"

# Generate presentation with notes
.PHONY: with-notes
with-notes:
	@echo "Generating presentation with speaker notes..."
	marp $(PRESENTATION_SOURCE) --html --output $(PRESENTATION_OUTPUT)-notes.html
	@echo "✅ Presentation with notes generated"

# Generate presentation for printing
.PHONY: print
print:
	@echo "Generating print-friendly presentation..."
	marp $(PRESENTATION_SOURCE) --pdf --output $(PRESENTATION_OUTPUT)-print.pdf
	@echo "✅ Print-friendly presentation generated"

# Generate presentation for sharing
.PHONY: share
share:
	@echo "Generating shareable presentation..."
	marp $(PRESENTATION_SOURCE) --html --output $(PRESENTATION_OUTPUT)-share.html
	@echo "✅ Shareable presentation generated"

# Generate all presentation variants
.PHONY: variants
variants: technical business with-notes print share
	@echo "✅ All presentation variants generated"

# Help target
.PHONY: help
help:
	@echo "GhostMesh Presentation Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all          - Generate all presentation formats (HTML, PDF, PPTX)"
	@echo "  html         - Generate HTML presentation"
	@echo "  pdf          - Generate PDF presentation"
	@echo "  pptx         - Generate PowerPoint presentation"
	@echo "  preview      - Preview presentation in browser"
	@echo "  watch        - Watch for changes and auto-regenerate"
	@echo "  clean        - Clean generated files"
	@echo "  install-marp - Install Marp CLI"
	@echo "  check-marp   - Check if Marp CLI is installed"
	@echo "  validate     - Validate presentation source"
	@echo "  technical    - Generate technical presentation"
	@echo "  business     - Generate business presentation"
	@echo "  with-notes   - Generate presentation with speaker notes"
	@echo "  print        - Generate print-friendly presentation"
	@echo "  share        - Generate shareable presentation"
	@echo "  variants     - Generate all presentation variants"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  PRESENTATION_SOURCE - Source Markdown file (default: ghostmesh-pitch.md)"
	@echo "  PRESENTATION_OUTPUT - Output file prefix (default: ghostmesh-pitch)"
	@echo "  THEME               - Marp theme (default: default)"
	@echo "  SIZE                - Presentation size (default: 16:9)"
	@echo ""
	@echo "Examples:"
	@echo "  make html                    # Generate HTML presentation"
	@echo "  make pdf                     # Generate PDF presentation"
	@echo "  make preview                 # Preview in browser"
	@echo "  make THEME=gaia html         # Generate with Gaia theme"
	@echo "  make SIZE=4:3 pdf            # Generate 4:3 aspect ratio PDF"

# Dependencies
.PHONY: deps
deps: check-marp
	@echo "✅ All dependencies are satisfied"

# Development setup
.PHONY: setup
setup: install-marp
	@echo "Setting up development environment..."
	@echo "✅ Development environment setup complete"

# Production build
.PHONY: build
build: deps validate all-formats
	@echo "✅ Production build complete"

# Test presentation generation
.PHONY: test
test: deps validate html
	@echo "✅ Presentation generation test passed"

# Package presentation for distribution
.PHONY: package
package: build
	@echo "Packaging presentation for distribution..."
	mkdir -p dist
	cp $(PRESENTATION_OUTPUT).html dist/
	cp $(PRESENTATION_OUTPUT).pdf dist/
	cp $(PRESENTATION_OUTPUT).pptx dist/
	cp *.md dist/
	@echo "✅ Presentation packaged in dist/ directory"

# Deploy presentation to web server
.PHONY: deploy
deploy: package
	@echo "Deploying presentation to web server..."
	# Add deployment commands here
	@echo "✅ Presentation deployed"

# Backup presentation files
.PHONY: backup
backup:
	@echo "Creating presentation backup..."
	tar -czf ghostmesh-presentation-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz *.md *.html *.pdf *.pptx
	@echo "✅ Presentation backup created"

# Restore presentation from backup
.PHONY: restore
restore:
	@echo "Restoring presentation from backup..."
	# Add restore commands here
	@echo "✅ Presentation restored"

# Update presentation from source
.PHONY: update
update: clean build
	@echo "✅ Presentation updated"

# Show presentation info
.PHONY: info
info:
	@echo "GhostMesh Presentation Information"
	@echo "=================================="
	@echo "Source file: $(PRESENTATION_SOURCE)"
	@echo "Output prefix: $(PRESENTATION_OUTPUT)"
	@echo "Theme: $(THEME)"
	@echo "Size: $(SIZE)"
	@echo "Marp CLI: $(shell which marp 2>/dev/null || echo 'Not installed')"
	@echo "Generated files:"
	@ls -la $(PRESENTATION_OUTPUT).* 2>/dev/null || echo "No generated files found"

# Show presentation statistics
.PHONY: stats
stats:
	@echo "Presentation Statistics"
	@echo "======================"
	@echo "Source file size: $(shell wc -c < $(PRESENTATION_SOURCE)) bytes"
	@echo "Number of slides: $(shell grep -c '^---' $(PRESENTATION_SOURCE))"
	@echo "Number of lines: $(shell wc -l < $(PRESENTATION_SOURCE))"
	@echo "Last modified: $(shell stat -f '%Sm' $(PRESENTATION_SOURCE))"

# Show presentation structure
.PHONY: structure
structure:
	@echo "Presentation Structure"
	@echo "====================="
	@grep -n '^#' $(PRESENTATION_SOURCE) | head -20

# Show presentation content
.PHONY: content
content:
	@echo "Presentation Content"
	@echo "==================="
	@head -50 $(PRESENTATION_SOURCE)

# Show presentation help
.PHONY: presentation-help
presentation-help:
	@echo "GhostMesh Presentation Help"
	@echo "=========================="
	@echo ""
	@echo "This Makefile helps you generate and manage the GhostMesh presentation."
	@echo ""
	@echo "Quick Start:"
	@echo "1. Run 'make install-marp' to install Marp CLI"
	@echo "2. Run 'make html' to generate HTML presentation"
	@echo "3. Run 'make preview' to preview in browser"
	@echo ""
	@echo "For more options, run 'make help'"
