#!/bin/bash
set -e

echo "🧪 Simple Auth API - Test Suite"
echo "================================"
echo ""
echo "Usage:"
echo "  ./run_tests.sh           # All tests (unit + integration)"
echo "  ./run_tests.sh --unit    # Unit tests only (fast, ~2s)"
echo "  ./run_tests.sh --integration # Integration tests only (PostgreSQL, ~2s)"
echo ""

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

# Handle different test modes
if [ "$1" = "--unit" ]; then
    print_info "Running unit tests only (fast, in-memory)..."
    python -m pytest -m unit -v --cov=src --cov-report=html --cov-report=term-missing
elif [ "$1" = "--integration" ]; then
    print_info "Running integration tests only (PostgreSQL)..."
    python -m pytest -m integration -v --cov=src --cov-report=html --cov-report=term-missing
else
    print_info "Running complete test suite with coverage..."
    python -m pytest -v --cov=src --cov-report=html --cov-report=term-missing
fi

if [ $? -eq 0 ]; then
    print_success "All tests passed!"
    print_info "Coverage report generated in htmlcov/"
else
    print_error "Some tests failed!"
    exit 1
fi

echo ""
print_success "Test execution completed!"
