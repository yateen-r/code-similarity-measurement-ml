import ast
import difflib
import re
from collections import Counter
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import lizard

try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Warning: tree-sitter not available. AST analysis will be limited.")


class MultiLanguageCodeAnalyzer:
    """Multi-language code analyzer with tree-sitter support"""
    
    def __init__(self):
        self.parsers = {}
        self.language_configs = {
            'python': {
                'extensions': ['.py'],
                'comment_patterns': [r'#.*', r'""".*?"""', r"'''.*?'''"],
                'string_patterns': [r'".*?"', r"'.*?'"],
                'function_patterns': [r'\bdef\s+\w+'],
                'class_patterns': [r'\bclass\s+\w+'],
                'loop_patterns': [r'\b(for|while)\b'],
                'conditional_patterns': [r'\b(if|elif|else)\b'],
                'import_patterns': [r'\b(import|from)\b'],
            },
            'java': {
                'extensions': ['.java'],
                'comment_patterns': [r'//.*', r'/\*.*?\*/'],
                'string_patterns': [r'".*?"'],
                'function_patterns': [r'(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\('],
                'class_patterns': [r'\bclass\s+\w+', r'\binterface\s+\w+'],
                'loop_patterns': [r'\b(for|while|do)\b'],
                'conditional_patterns': [r'\b(if|else|switch)\b'],
                'import_patterns': [r'\bimport\b'],
            },
            'javascript': {
                'extensions': ['.js', '.jsx'],
                'comment_patterns': [r'//.*', r'/\*.*?\*/'],
                'string_patterns': [r'".*?"', r"'.*?'", r'`.*?`'],
                'function_patterns': [r'\bfunction\s+\w+', r'\w+\s*=\s*\(.*?\)\s*=>', r'\w+\s*:\s*function'],
                'class_patterns': [r'\bclass\s+\w+'],
                'loop_patterns': [r'\b(for|while|do)\b'],
                'conditional_patterns': [r'\b(if|else|switch)\b'],
                'import_patterns': [r'\b(import|require)\b'],
            },
            'cpp': {
                'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
                'comment_patterns': [r'//.*', r'/\*.*?\*/'],
                'string_patterns': [r'".*?"'],
                'function_patterns': [r'\w+\s+\w+\s*\('],
                'class_patterns': [r'\bclass\s+\w+', r'\bstruct\s+\w+'],
                'loop_patterns': [r'\b(for|while|do)\b'],
                'conditional_patterns': [r'\b(if|else|switch)\b'],
                'import_patterns': [r'#include'],
            },
            'c': {
                'extensions': ['.c', '.h'],
                'comment_patterns': [r'//.*', r'/\*.*?\*/'],
                'string_patterns': [r'".*?"'],
                'function_patterns': [r'\w+\s+\w+\s*\('],
                'class_patterns': [r'\bstruct\s+\w+'],
                'loop_patterns': [r'\b(for|while|do)\b'],
                'conditional_patterns': [r'\b(if|else|switch)\b'],
                'import_patterns': [r'#include'],
            },
        }
        
        # Initialize tree-sitter if available
        if TREE_SITTER_AVAILABLE:
            self._initialize_tree_sitter()
    
    def _initialize_tree_sitter(self):
        """Initialize tree-sitter parsers for each language"""
        try:
            # Note: In production, you need to build language libraries first
            # See setup instructions at the end
            pass
        except Exception as e:
            print(f"Tree-sitter initialization warning: {e}")
    
    def get_language_config(self, language):
        """Get configuration for specified language"""
        return self.language_configs.get(language.lower(), self.language_configs['python'])


class CodeSimilarityAnalyzer:
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'\b\w+\b',
            lowercase=True,
            max_features=1000
        )
        self.language_analyzer = MultiLanguageCodeAnalyzer()
    
    def analyze_similarity(self, source_code, target_code, language='python'):
        """Main method to analyze code similarity for any supported language"""
        results = {
            'overall_similarity': 0.0,
            'structural_similarity': 0.0,
            'token_similarity': 0.0,
            'ast_similarity': 0.0,
            'identical_segments': [],
            'near_identical_segments': [],
            'code_metrics': {}
        }
        
        try:
            language = language.lower()
            
            # Token-based similarity (language-agnostic)
            results['token_similarity'] = self._token_similarity(source_code, target_code, language)
            
            # Structural similarity (language-specific)
            results['structural_similarity'] = self._structural_similarity(source_code, target_code, language)
            
            # AST similarity (language-specific)
            results['ast_similarity'] = self._ast_similarity(source_code, target_code, language)
            
            # Find identical and near-identical segments
            results['identical_segments'], results['near_identical_segments'] = \
                self._find_similar_segments(source_code, target_code)
            
            # Calculate overall similarity (weighted average)
            weights = {'token': 0.3, 'structural': 0.3, 'ast': 0.4}
            results['overall_similarity'] = (
                results['token_similarity'] * weights['token'] +
                results['structural_similarity'] * weights['structural'] +
                results['ast_similarity'] * weights['ast']
            )
            
            # Code metrics comparison
            results['code_metrics'] = self._calculate_metrics_comparison(source_code, target_code, language)
            
        except Exception as e:
            print(f"Error in similarity analysis: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _token_similarity(self, code1, code2, language):
        """Calculate token-based similarity using TF-IDF (language-agnostic)"""
        try:
            # Tokenize code with language-specific cleanup
            tokens1 = self._tokenize_code(code1, language)
            tokens2 = self._tokenize_code(code2, language)
            
            if not tokens1 or not tokens2:
                return 0.0
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([tokens1, tokens2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"Token similarity error: {e}")
            # Fallback to simple sequence matcher
            return difflib.SequenceMatcher(None, code1, code2).ratio()
    
    def _structural_similarity(self, code1, code2, language):
        """Calculate structural similarity based on language-specific patterns"""
        try:
            # Extract structural features
            features1 = self._extract_structural_features(code1, language)
            features2 = self._extract_structural_features(code2, language)
            
            # Compare features
            similarities = []
            for key in features1:
                if key in features2:
                    if features1[key] == 0 and features2[key] == 0:
                        similarities.append(1.0)
                    else:
                        max_val = max(features1[key], features2[key])
                        min_val = min(features1[key], features2[key])
                        similarities.append(min_val / max_val if max_val > 0 else 0)
            
            return np.mean(similarities) if similarities else 0.0
        except Exception as e:
            print(f"Structural similarity error: {e}")
            return 0.0
    
    def _ast_similarity(self, code1, code2, language):
        """Calculate AST-based similarity (language-specific)"""
        try:
            if language == 'python':
                return self._python_ast_similarity(code1, code2)
            elif language in ['java', 'javascript', 'cpp', 'c']:
                return self._generic_ast_similarity(code1, code2, language)
            else:
                return 0.0
        except Exception as e:
            print(f"AST similarity error: {e}")
            return 0.0
    
    def _python_ast_similarity(self, code1, code2):
        """Python-specific AST similarity using built-in ast module"""
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)
            
            # Get AST node types
            nodes1 = [type(node).__name__ for node in ast.walk(tree1)]
            nodes2 = [type(node).__name__ for node in ast.walk(tree2)]
            
            # Calculate similarity using sequence matcher
            similarity = difflib.SequenceMatcher(None, nodes1, nodes2).ratio()
            
            return float(similarity)
        except Exception as e:
            print(f"Python AST error: {e}")
            return 0.0
    
    def _generic_ast_similarity(self, code1, code2, language):
        """Generic AST similarity for non-Python languages"""
        try:
            # Use lizard for complexity-based comparison
            analyzer1 = lizard.analyze_file.analyze_source_code("file1", code1)
            analyzer2 = lizard.analyze_file.analyze_source_code("file2", code2)
            
            # Compare function signatures and complexity
            funcs1 = {f.name: f.cyclomatic_complexity for f in analyzer1.function_list}
            funcs2 = {f.name: f.cyclomatic_complexity for f in analyzer2.function_list}
            
            # Calculate similarity based on function names and complexity
            common_funcs = set(funcs1.keys()) & set(funcs2.keys())
            all_funcs = set(funcs1.keys()) | set(funcs2.keys())
            
            if not all_funcs:
                return 0.0
            
            name_similarity = len(common_funcs) / len(all_funcs)
            
            # Complexity similarity for common functions
            complexity_similarities = []
            for func_name in common_funcs:
                c1 = funcs1[func_name]
                c2 = funcs2[func_name]
                if c1 == 0 and c2 == 0:
                    complexity_similarities.append(1.0)
                else:
                    complexity_similarities.append(min(c1, c2) / max(c1, c2))
            
            complexity_similarity = np.mean(complexity_similarities) if complexity_similarities else 0.0
            
            # Weighted average
            return (name_similarity * 0.6 + complexity_similarity * 0.4)
            
        except Exception as e:
            print(f"Generic AST error: {e}")
            return 0.0
    
    def _find_similar_segments(self, code1, code2, threshold=0.9):
        """Find identical and near-identical code segments"""
        identical = []
        near_identical = []
        
        lines1 = code1.splitlines()
        lines2 = code2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal' and (i2 - i1) >= 3:  # At least 3 lines
                identical.append({
                    'source_start': i1 + 1,
                    'source_end': i2,
                    'target_start': j1 + 1,
                    'target_end': j2,
                    'lines': i2 - i1,
                    'content': '\n'.join(lines1[i1:i2])
                })
            elif tag == 'replace' and (i2 - i1) >= 3:
                segment1 = '\n'.join(lines1[i1:i2])
                segment2 = '\n'.join(lines2[j1:j2])
                sim = difflib.SequenceMatcher(None, segment1, segment2).ratio()
                
                if sim >= threshold:
                    near_identical.append({
                        'source_start': i1 + 1,
                        'source_end': i2,
                        'target_start': j1 + 1,
                        'target_end': j2,
                        'lines': i2 - i1,
                        'similarity': sim
                    })
        
        return identical, near_identical
    
    def _tokenize_code(self, code, language):
        """Tokenize code into meaningful tokens (language-specific)"""
        config = self.language_analyzer.get_language_config(language)
        
        # Remove comments
        for pattern in config['comment_patterns']:
            code = re.sub(pattern, '', code, flags=re.DOTALL)
        
        # Remove strings
        for pattern in config['string_patterns']:
            code = re.sub(pattern, '', code)
        
        # Extract tokens
        tokens = re.findall(r'\b\w+\b', code)
        return ' '.join(tokens)
    
    def _extract_structural_features(self, code, language):
        """Extract structural features based on language"""
        config = self.language_analyzer.get_language_config(language)
        
        features = {
            'functions': len(re.findall(config['function_patterns'][0], code)),
            'classes': len(re.findall(config['class_patterns'][0], code)) if config['class_patterns'] else 0,
            'loops': len(re.findall(config['loop_patterns'][0], code)),
            'conditionals': len(re.findall(config['conditional_patterns'][0], code)),
            'imports': len(re.findall(config['import_patterns'][0], code)),
        }
        
        # Language-specific features
        if language == 'python':
            features['try_except'] = len(re.findall(r'\btry\b', code))
            features['returns'] = len(re.findall(r'\breturn\b', code))
        elif language == 'java':
            features['try_catch'] = len(re.findall(r'\btry\b', code))
            features['returns'] = len(re.findall(r'\breturn\b', code))
            features['interfaces'] = len(re.findall(r'\binterface\s+\w+', code))
        elif language == 'javascript':
            features['arrow_functions'] = len(re.findall(r'=>', code))
            features['returns'] = len(re.findall(r'\breturn\b', code))
        elif language in ['cpp', 'c']:
            features['pointers'] = len(re.findall(r'\*\w+', code))
            features['returns'] = len(re.findall(r'\breturn\b', code))
        
        return features
    
    def _calculate_metrics_comparison(self, code1, code2, language):
        """Calculate and compare code metrics"""
        metrics1 = self._calculate_single_metrics(code1, language)
        metrics2 = self._calculate_single_metrics(code2, language)
        
        return {
            'source_metrics': metrics1,
            'target_metrics': metrics2,
            'complexity_diff': abs(metrics1['complexity'] - metrics2['complexity']),
            'loc_diff': abs(metrics1['loc'] - metrics2['loc'])
        }
    
    def _calculate_single_metrics(self, code, language):
        """Calculate metrics for a single code file"""
        try:
            if language == 'python':
                # Use radon for Python
                analysis = analyze(code)
                return {
                    'loc': analysis.loc,
                    'lloc': analysis.lloc,
                    'sloc': analysis.sloc,
                    'comments': analysis.comments,
                    'blank': analysis.blank,
                    'complexity': self._calculate_complexity(code, language)
                }
            else:
                # Use lizard for other languages
                analysis = lizard.analyze_file.analyze_source_code("temp", code)
                return {
                    'loc': analysis.nloc,
                    'lloc': analysis.nloc,
                    'sloc': analysis.nloc,
                    'comments': 0,  # Lizard doesn't provide this
                    'blank': 0,
                    'complexity': np.mean([f.cyclomatic_complexity for f in analysis.function_list]) if analysis.function_list else 0
                }
        except Exception as e:
            print(f"Metrics calculation error: {e}")
            return {
                'loc': len(code.splitlines()),
                'lloc': 0,
                'sloc': 0,
                'comments': 0,
                'blank': 0,
                'complexity': 0
            }
    
    def _calculate_complexity(self, code, language):
        """Calculate cyclomatic complexity"""
        try:
            if language == 'python':
                complexity_list = cc_visit(code)
                if complexity_list:
                    return np.mean([item.complexity for item in complexity_list])
            else:
                analysis = lizard.analyze_file.analyze_source_code("temp", code)
                if analysis.function_list:
                    return np.mean([f.cyclomatic_complexity for f in analysis.function_list])
            return 0
        except Exception as e:
            print(f"Complexity calculation error: {e}")
            return 0


class MLSimilarityPredictor:
    """Machine Learning based similarity prediction"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.model_path = model_path
        if model_path:
            self._load_model()
    
    def _load_model(self):
        """Load trained ML model"""
        import joblib
        try:
            self.model = joblib.load(self.model_path)
        except Exception as e:
            print(f"Model loading error: {e}")
            self.model = None
    
    def predict_similarity(self, features):
        """Predict similarity using ML model"""
        if self.model is None:
            return None
        
        try:
            prediction = self.model.predict([features])[0]
            return float(prediction)
        except Exception as e:
            print(f"Prediction error: {e}")
            return None
    
    def extract_ml_features(self, code1, code2, basic_similarities):
        """Extract features for ML prediction"""
        features = [
            basic_similarities['token_similarity'],
            basic_similarities['structural_similarity'],
            basic_similarities['ast_similarity'],
            len(basic_similarities['identical_segments']),
            len(basic_similarities['near_identical_segments']),
            basic_similarities['code_metrics']['complexity_diff'],
            basic_similarities['code_metrics']['loc_diff'],
        ]
        return features
