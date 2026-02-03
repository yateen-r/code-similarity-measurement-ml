from django.core.management.base import BaseCommand
from similarity_engine.similarity_analyzer import CodeSimilarityAnalyzer

class Command(BaseCommand):
    help = 'Test multi-language code similarity analysis'
    
    def handle(self, *args, **options):
        analyzer = CodeSimilarityAnalyzer()
        
        # Test Python
        python_code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        python_code2 = """
def fib(num):
    if num <= 1:
        return num
    return fib(num-1) + fib(num-2)
"""
        
        self.stdout.write(self.style.SUCCESS('\n=== Testing Python ==='))
        result = analyzer.analyze_similarity(python_code1, python_code2, 'python')
        self.stdout.write(f"Overall Similarity: {result['overall_similarity']:.2%}")
        self.stdout.write(f"Token: {result['token_similarity']:.2%}, Structural: {result['structural_similarity']:.2%}, AST: {result['ast_similarity']:.2%}")
        
        # Test Java
        java_code1 = """
public class Fibonacci {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
}
"""
        java_code2 = """
public class Fib {
    public static int fib(int num) {
        if (num <= 1) return num;
        return fib(num-1) + fib(num-2);
    }
}
"""
        
        self.stdout.write(self.style.SUCCESS('\n=== Testing Java ==='))
        result = analyzer.analyze_similarity(java_code1, java_code2, 'java')
        self.stdout.write(f"Overall Similarity: {result['overall_similarity']:.2%}")
        self.stdout.write(f"Token: {result['token_similarity']:.2%}, Structural: {result['structural_similarity']:.2%}, AST: {result['ast_similarity']:.2%}")
        
        # Test JavaScript
        js_code1 = """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
"""
        js_code2 = """
const fib = (num) => {
    if (num <= 1) return num;
    return fib(num-1) + fib(num-2);
};
"""
        
        self.stdout.write(self.style.SUCCESS('\n=== Testing JavaScript ==='))
        result = analyzer.analyze_similarity(js_code1, js_code2, 'javascript')
        self.stdout.write(f"Overall Similarity: {result['overall_similarity']:.2%}")
        self.stdout.write(f"Token: {result['token_similarity']:.2%}, Structural: {result['structural_similarity']:.2%}, AST: {result['ast_similarity']:.2%}")
        
        # Test C++
        cpp_code1 = """
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
"""
        cpp_code2 = """
int fib(int num) {
    if (num <= 1) return num;
    return fib(num-1) + fib(num-2);
}
"""
        
        self.stdout.write(self.style.SUCCESS('\n=== Testing C++ ==='))
        result = analyzer.analyze_similarity(cpp_code1, cpp_code2, 'cpp')
        self.stdout.write(f"Overall Similarity: {result['overall_similarity']:.2%}")
        self.stdout.write(f"Token: {result['token_similarity']:.2%}, Structural: {result['structural_similarity']:.2%}, AST: {result['ast_similarity']:.2%}")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Multi-language testing completed!'))
