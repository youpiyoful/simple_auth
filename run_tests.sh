#!/bin/bash
set -e

echo "🧪 Simple Auth API - Test Suite"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Install base and test dependencies
print_info "Installing base dependencies..."
pip install -r requirements.txt

print_info "Installing test dependencies..."
pip install -r requirements-test.txt

# Run tests with coverage
print_info "Running test suite with coverage..."
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

if [ $? -eq 0 ]; then
    print_success "All tests passed!"
    print_info "Coverage report generated in htmlcov/"
else
    print_error "Some tests failed!"
    exit 1
fi

# Optional: Run specific test categories
if [ "$1" = "--integration" ]; then
    print_info "Running integration tests..."
    python -m pytest tests/ -v -k "integration"
fi

if [ "$1" = "--unit" ]; then
    print_info "Running unit tests only..."
    python -m pytest tests/ -v -k "not integration"
fi

echo ""
print_success "Test execution completed!"
