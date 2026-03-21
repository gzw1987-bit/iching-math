# The King Wen Permutation: [52, 10, 2]

**The cycle decomposition of the permutation mapping between the binary natural order and the King Wen sequence of the I Ching's 64 hexagrams.**

## The Discovery

The 64 hexagrams of the I Ching admit two classical orderings: the binary natural order (Shao Yong / Fu Xi sequence) and the received King Wen sequence. Treating the King Wen sequence as a permutation in S₆₄, its cycle decomposition yields the type **(52, 10, 2)** — a single dominant cycle containing 52 of 64 hexagrams (81.25%), a secondary 10-cycle, and one transposition. There are zero fixed points. This cycle structure has not been previously reported in the mathematical or sinological literature.

## Key Results

- **Cycle type:** (52, 10, 2)
- **Fixed points:** 0
- **Largest cycle:** 52 (81.25% of all hexagrams)
- **Order:** lcm(52, 10, 2) = 260
- **Mean Hamming distance:** 3.349 (random baseline: 3.0)
- **Even:odd permutation ratio:** 3.2:1

## Live Demo

**[https://[username].github.io/iching-math/](https://[username].github.io/iching-math/)**

- [Verify it yourself](verify-permutation.html) — interactive cycle decomposition tool
- [Watch the algorithm](algorithm-animation.html) — step-by-step animation
- [Full derivation journey](derivation-journey.html) — 13-stage interactive visualization (Chinese)

## Paper

"The Cycle Structure of the King Wen Permutation" by Zhengwen Ge (2026). Available in:

- [Interactive English version](paper-en.html) — read in browser, zero dependencies
- [Interactive Chinese version](permutation-cycle-paper.html) — 中文交互式论文
- [LaTeX source](paper/main.tex) — for arXiv/Zenodo submission

## Reproduce

```bash
# Verify the cycle decomposition (Node.js or browser console)
node -e "const W=[2,23,8,20,16,35,45,12,15,52,39,53,62,56,31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,28,44,24,27,3,42,51,21,17,25,36,22,63,37,55,30,49,13,19,41,60,61,54,38,58,10,11,26,5,9,34,14,43,1];const p=W.map(w=>w-1),v=new Set,c=[];for(let i=0;i<64;i++){if(v.has(i))continue;const y=[];let j=i;while(!v.has(j)){v.add(j);y.push(j);j=p[j]}c.push(y)}console.log(c.map(x=>x.length).sort((a,b)=>b-a))"
# Output: [ 52, 10, 2 ]

# Run Monte Carlo simulation (Python 3)
python3 monte_carlo.py
```

## Historical Note

> The binary natural order was formalized by Shao Yong (1011-1077 CE), approximately 2,000 years after King Wen (~1100 BCE). We do not claim King Wen "rearranged" the binary order. This analysis measures the structural distance between two independently defined orderings.

## Project Contents

### Discovery & Verification

| File | Description |
|------|-------------|
| [verify-permutation.html](verify-permutation.html) | Interactive cycle decomposition tool |
| [algorithm-animation.html](algorithm-animation.html) | Step-by-step permutation algorithm animation |
| [monte_carlo.py](monte_carlo.py) | Monte Carlo simulation for statistical baselines |
| [verify.py](verify.py) | Python verification script |

### Derivation Journey

| File | Description |
|------|-------------|
| [derivation-journey.html](derivation-journey.html) | 13-stage interactive visualization (Chinese) |
| [permutation-cycle-paper.html](permutation-cycle-paper.html) | Interactive paper (Chinese) |
| [paper/main.tex](paper/main.tex) | LaTeX source of the formal paper |

### Binary Structure Explorations

| File | Description |
|------|-------------|
| [binary-yaoci.html](binary-yaoci.html) | Binary yao-line analysis |
| [bit-arrangements.html](bit-arrangements.html) | Bit arrangement patterns |
| [bit-forms.html](bit-forms.html) | Bit form visualizations |
| [bit-music.html](bit-music.html) | Hexagram-to-music sonification |
| [bit-morse.html](bit-morse.html) | Hexagram-to-Morse mapping |
| [bit-voltage.html](bit-voltage.html) | Voltage signal representation |

### Cross-Disciplinary

| File | Description |
|------|-------------|
| [wave-compare.html](wave-compare.html) | Kondratieff wave x DJIA x hexagram timeline (1780-2026) |
| [genome_analysis.py](genome_analysis.py) | Genomic sequence analysis |
| [genome-view.html](genome-view.html) | Genome visualization |
| [game-theory.html](game-theory.html) | Game-theoretic analysis |
| [coupled-cycles.html](coupled-cycles.html) | Coupled cycle dynamics |
| [coupled-system.html](coupled-system.html) | Coupled system visualization |

### Architecture & Meta

| File | Description |
|------|-------------|
| [engine-architecture.html](engine-architecture.html) | Engine architecture visualization |
| [four-minds.html](four-minds.html) | Four-minds framework |
| [strategy-debate.html](strategy-debate.html) | Strategy debate simulation |
| [deep-diagnostic.html](deep-diagnostic.html) | Deep diagnostic tool |
| [shang-timeline.html](shang-timeline.html) | Shang dynasty timeline |

## License

MIT (code) / CC BY 4.0 (written content). See [LICENSE](LICENSE).

## Citation

```bibtex
@misc{ge2026kingwen,
  author = {Ge, Zhengwen},
  title = {The Cycle Structure of the King Wen Permutation: A Group-Theoretic Analysis of Two Classical Hexagram Orderings},
  year = {2026},
  doi = {10.5281/zenodo.19143997},
  url = {https://doi.org/10.5281/zenodo.19143997}
}
```
