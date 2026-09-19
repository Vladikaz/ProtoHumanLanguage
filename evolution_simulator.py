import os, sys, sqlite3, argparse, re, math, json
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


sys.stdout.reconfigure(encoding='utf-8')

TARGET_DIR = DATA_DIR
PHASE2_DB = os.path.join(TARGET_DIR, "phase2.db")

IPA_MULTI = sorted([
    'tʃ', 'dʒ', 'tɕ', 'dʑ', 'ts', 'dz', 'kp', 'gb', 'pf', 'bv',
    'pʰ', 'tʰ', 'kʰ', 'qʰ', 'p\'', 't\'', 'k\'', 'q\'',
    'kʷ', 'gʷ', 'xʷ', 'ɣʷ', 'qʷ', 'ŋʷ', 'wʷ', 'hʷ',
    'aː', 'eː', 'iː', 'oː', 'uː', 'yː', 'æː', 'øː', 'əː',
    'ã', 'ẽ', 'ĩ', 'õ', 'ũ',
    'r̥', 'l̥', 'm̥', 'n̥', 'ŋ', 'ɲ', 'ɳ', 'ʈ', 'ɖ', 'ɕ', 'ʑ', 'ɣ', 'x', 'χ', 'ʁ', 'ʕ', 'ħ', 'ʔ',
], key=len, reverse=True)

def segment_word(word):
    if not word:
        return []
    w = str(word).strip()
    w = re.sub(r'[\*\(\)\[\]\{\}\?\#\$\`\'\"]', '', w).strip()
    if not w:
        return []
    if ' ' in w:
        return w.split()
    tokens = []
    i = 0
    while i < len(w):
        matched = False
        for symbol in IPA_MULTI:
            if w.startswith(symbol, i):
                tokens.append(symbol)
                i += len(symbol)
                matched = True
                break
        if not matched:
            tokens.append(w[i])
            i += 1
    return tokens

class PhoneticEvolutionSimulator:
    def __init__(self, db_path=PHASE2_DB):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()
        self._load_matrices()
        
    def _load_matrices(self):
        self.laws_by_context = {}
        self.marginal_matrix = {}
        self.bayes_reverse = {}
        
        self.c.execute("SELECT source_seg, target_seg, context_class, probability, rate_per_1000y, phonetic_process FROM universal_laws")
        for src, tgt, ctx, prob, rate, proc in self.c.fetchall():
            key = (src, ctx)
            if key not in self.laws_by_context:
                self.laws_by_context[key] = []
            self.laws_by_context[key].append((tgt, prob, rate, proc))
            
        self.c.execute("SELECT source_seg, target_seg, marginal_probability FROM phoneme_transition_matrix")
        for src, tgt, prob in self.c.fetchall():
            if src not in self.marginal_matrix:
                self.marginal_matrix[src] = []
            self.marginal_matrix[src].append((tgt, prob))
            
            if tgt not in self.bayes_reverse:
                self.bayes_reverse[tgt] = []
            self.bayes_reverse[tgt].append((src, prob))

    def simulate_forward(self, word, years=1000.0, top_k=5):
        segments = segment_word(word)
        if not segments:
            return [("Could not parse input word", 0.0, [])]
            
        time_factor = years / 1000.0
        
        # State: list of (current_sequence, probability, change_log)
        states = [(segments, 1.0, [])]
        
        # Process phonemes position by position
        for pos_idx in range(len(segments)):
            next_states = []
            for curr_seq, curr_prob, log in states:
                if pos_idx >= len(curr_seq):
                    next_states.append((curr_seq, curr_prob, log))
                    continue
                    
                src = curr_seq[pos_idx]
                left_ctx = curr_seq[pos_idx-1] if pos_idx > 0 else '#'
                right_ctx = curr_seq[pos_idx+1] if pos_idx < len(curr_seq)-1 else '#'
                
                pos_cls = 'medial'
                if left_ctx == '#': pos_cls = '#_'
                elif right_ctx == '#': pos_cls = '_#'
                
                rules = self.laws_by_context.get((src, pos_cls), [])
                if not rules:
                    rules = self.laws_by_context.get((src, 'medial'), [])
                if not rules:
                    rules = self.marginal_matrix.get(src, [])
                    
                if not rules:
                    next_states.append((curr_seq, curr_prob, log))
                    continue
                    
                sum_change_prob = 0.0
                options = []
                for item in rules:
                    if len(item) == 4:
                        tgt, prob, rate, proc = item
                    else:
                        tgt, prob = item; proc = "Marginal shift"
                        
                    eff_prob = min(0.9, prob * time_factor)
                    if tgt != src:
                        sum_change_prob += eff_prob
                        options.append((tgt, eff_prob, proc))
                        
                stay_prob = max(0.1, 1.0 - sum_change_prob)
                options.append((src, stay_prob, "Stability"))
                options.sort(key=lambda x: x[1], reverse=True)
                
                for tgt, p_opt, proc in options[:3]:
                    mod_seq = list(curr_seq)
                    new_log = list(log)
                    
                    if tgt == '∅':
                        mod_seq.pop(pos_idx)
                        new_log.append(f"Pos {pos_idx+1} ({src} -> ∅): {proc}")
                    elif tgt != src:
                        mod_seq[pos_idx] = tgt
                        new_log.append(f"Pos {pos_idx+1} ({src} -> {tgt}): {proc}")
                        
                    next_states.append((mod_seq, curr_prob * p_opt, new_log))
                    
            next_states.sort(key=lambda x: x[1], reverse=True)
            states = next_states[:10]
            
        results = []
        for seq, prob, log in states[:top_k]:
            out_word = "".join(seq) if seq else "∅"
            results.append((out_word, round(prob, 4), log))
        return results

    def reconstruct_backward(self, word, years=1000.0, top_k=5):
        segments = segment_word(word)
        if not segments:
            return [("Could not parse input word", 0.0, [])]
            
        states = [(segments, 1.0, [])]
        
        for pos_idx in range(len(segments)):
            next_states = []
            for curr_seq, curr_prob, log in states:
                if pos_idx >= len(curr_seq):
                    next_states.append((curr_seq, curr_prob, log))
                    continue
                    
                tgt = curr_seq[pos_idx]
                possible_sources = self.bayes_reverse.get(tgt, [(tgt, 0.8)])
                
                for src, p_rev in possible_sources[:3]:
                    mod_seq = list(curr_seq)
                    mod_seq[pos_idx] = src
                    new_log = list(log)
                    if src != tgt:
                        new_log.append(f"Pos {pos_idx+1} (*{src} -> {tgt})")
                    next_states.append((mod_seq, curr_prob * p_rev, new_log))
                    
            next_states.sort(key=lambda x: x[1], reverse=True)
            states = next_states[:10]
            
        results = []
        for seq, prob, log in states[:top_k]:
            out_word = "*" + "".join(seq)
            results.append((out_word, round(prob, 4), log))
        return results

    def close(self):
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description="Phonetic Evolution Simulator & Retro-prediction Engine")
    parser.add_argument("--word", type=str, help="Word to evolve forward (e.g. *pater, *kwo)")
    parser.add_argument("--reconstruct", type=str, help="Word to reconstruct backward (e.g. father, cent)")
    parser.add_argument("--years", type=float, default=1000.0, help="Elapsed time in years (default: 1000)")
    parser.add_argument("--top", type=int, default=5, help="Number of top candidates to output")
    
    args = parser.parse_args()
    
    if not args.word and not args.reconstruct:
        print("=== PHONETIC EVOLUTION SIMULATOR DEMO ===")
        sim = PhoneticEvolutionSimulator()
        
        demo_words = ["*pater", "*kwo", "centum", "*wódr̥"]
        for w in demo_words:
            print(f"\n[FORWARD EVOLUTION] Input: '{w}' across 2000 years:")
            res = sim.simulate_forward(w, years=2000.0, top_k=3)
            for out_w, prob, log in res:
                print(f"  -> '{out_w:15}' (Prob: {prob:.4f})")
                for item in log:
                    print(f"       * {item}")
                    
        demo_retro = ["father", "cent", "water"]
        for w in demo_retro:
            print(f"\n[BACKWARD RECONSTRUCTION] Modern input: '{w}':")
            res = sim.reconstruct_backward(w, years=2000.0, top_k=3)
            for out_w, prob, log in res:
                print(f"  -> '{out_w:15}' (Posterior Prob: {prob:.4f})")
                
        sim.close()
        return

    sim = PhoneticEvolutionSimulator()
    if args.word:
        print(f"=== FORWARD EVOLUTION: '{args.word}' over {args.years:.0f} years ===")
        res = sim.simulate_forward(args.word, years=args.years, top_k=args.top)
        for out_w, prob, log in res:
            print(f"-> Form: '{out_w:15}' | Probability: {prob:.4f}")
            for item in log:
                print(f"     {item}")
                
    if args.reconstruct:
        print(f"=== BACKWARD RECONSTRUCTION: '{args.reconstruct}' ===")
        res = sim.reconstruct_backward(args.reconstruct, years=args.years, top_k=args.top)
        for out_w, prob, log in res:
            print(f"-> Proto-Form: '{out_w:15}' | Posterior Prob: {prob:.4f}")
            for item in log:
                print(f"     {item}")
                
    sim.close()

if __name__ == "__main__":
    main()