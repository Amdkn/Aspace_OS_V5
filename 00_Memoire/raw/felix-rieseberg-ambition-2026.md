# How to Be More Ambitious: A Tutorial for Humans with Models — Felix Rieseberg (13 Oct 2026)

- **Source URL** : https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/
- **Author** : Felix Rieseberg (Engineering Manager at Anthropic — Claude.ai, Cowork, Claude Code Desktop; Co-maintainer of Electron)
- **Visual Anchor** : Francisco Goya, *"Modo de volar"* (A Way of Flying)

## 1. The 4 Vectors of Ambition with Models
Model capabilities do not grow uniformly ("astounding in some directions, while inadequate in others" — Terence Tao). Ambition with models breaks down into four orthogonal dimensions:
1. **Speed (Vitesse)** : Doing the same work in less time. The baseline economic value of AI.
2. **Altitude (Élévation d'abstraction)** : Going up in abstraction and targeting the ultimate outcome rather than the individual task (*"What do you want to happen next? What's the goal beyond the goal?"*).
   - Example transition: Instead of asking the model to fix individual crashes, ask it to keep the apps crash-free.
   - Instead of filling a QBR deck template, feed raw business history and ask:
     1. *"Tell me what changed this quarter, why, and what we should do about it."*
     2. *"Work out which three decisions are most urgent in the face of everything you've learned, and start working on potential directions with for/against arguments."*
     3. *"Design a better way to catch problems early and move money and people to the right places than a quarterly deck, show from our own history that it would have caught things sooner, and run it beside the current one."*
3. **Depth (Profondeur d'expert & Juge externe)** : Approaching a task the way a field-leading expert would, touching the rawest underlying data, tools, and problems rather than switching vocabulary.
   - **Insist on industry-grade instruments** : Refuse markdown tables when databases, statistical models, ASTs, or simulations are warranted.
   - **Pick unreasonable goals and frame them as reasonable** : Need 5s instead of 10s? Ask for 200ms. Reiterate that it is solvable and the agent must keep going.
   - **Challenge what you know** : Adversarially test human assumptions against raw logs and primary data.
   - **Produce new knowledge** : Build a simulation from historical logs, find the earliest predictive signal of failure/churn not yet known, and validate it on unseen data.
   - **Use an outside judge (Never let the model judge itself)** : Always enforce external, deterministic validation (test suites, compilers, benchmarks, receipts).
   - **The 4-Step Depth Meta-Prompt** :
     > "I want a deeper version of this task, not a bigger one. Before rewriting it: (1) say what a top professional in this field would do here that I'm not asking for; (2) name the rawest material they would start from instead of what has already been digested for me; (3) name the specific methods and tools they would use; (4) say what, other than you or me, would show the result is right. Then rewrite my prompt to ask for exactly that."
4. **Range (Portée transdisciplinaire)** : Drawing on multiple fields simultaneously using multi-agent crews and real disciplinary methods.
   - **Replace nouns with verbs** (*The Art of Innovation*, Tom Kelley) : Redefine the artifact by the verb of its real-world effect (e.g., not "a deck", but "getting busy decision-makers to understand cause and effect and decide under uncertainty in 30 minutes").
   - **Assemble the crew (Methods, not Roleplay)** : Bring together an analyst, journalist, editor, motion/audio designer, plus an adversarial Red Team (short seller, forensic accountant). **Crucial rule**: Do not ask the model to *write like* a short seller; ask it to *do what a short seller does* to research their position.

## 2. Hacking Self-Efficacy (Psychology of Ambition)
- **Locke & Latham (35 years of goal-setting research)** : Specific, hard goals consistently outperform "try your best".
- **Patrick Collison's "Fast" list** : Audacious goals + tight deadlines unlock disproportionate execution.
- **George Dantzig Effect (1939)** : Solving two famous unsolved statistics problems because he thought they were homework — believing a hard problem is solvable removes self-imposed ceilings.
- **Roger Bannister Effect (1954 / Sabastian Sawe 2026)** : Once one system proves a boundary can be broken, others break it immediately.
- **The Inner Game of Tennis / Linux** : Giving the system permission to iterate boldly without ego friction.
