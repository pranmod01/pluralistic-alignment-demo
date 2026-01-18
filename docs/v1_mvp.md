# V1 - MVP

## Decision Tree for MVP

```
START: User submits query
│
├─> Is topic relevant to ANY community user belongs to?
│   ├─> NO → Standard response (no perspective surfacing)
│   └─> YES → Continue
│
├─> Does controversy exist WITHIN user's communities?
│   ├─> YES → Surface perspectives within same community
│   └─> NO → Continue
│
├─> Does controversy exist ACROSS communities user might engage with?
│   ├─> NO → Standard response
│   └─> YES → Continue
│
├─> Are there strongly held differing views?
│   ├─> NO → Standard response (mention existence of other views casually)
│   └─> YES → SURFACE MULTIPLE PERSPECTIVES
│
└─> Selection logic:
    ├─> Include user's own community perspective (baseline)
    ├─> Include 1-2 other communities based on:
    │   ├─> Geographic relevance
    │   ├─> Proximity to user's communities
    │   └─> Significance of cleavage on this specific issue
    └─> Frame as "perspectives from [community]" explicitly
```

## Technical Setup

```
User Query
    ↓
[Community Inference] ← Survey results cached
    ↓
[Controversy Detection] ← Query + User communities → Binary: Surface perspectives?
    ↓
[If YES] → [Community Selection] ← Query + Controversy profile → Which communities to include?
    ↓
[Perspective Generation]
    ├─> Consistency cache check: Have we answered this community-topic before?
    ├─> If cached: Return stored perspective framing
    └─> If new: Generate + store in cache
    ↓
[Response Assembly]
    ├─> User's community perspective (baseline)
    ├─> Other community perspectives (1-2)
    └─> Frame with explicit community labels
    ↓
Response to User
```

### Technical Details

**Caching Strategy:**
- Cache key: `hash(community_affiliation, topic, perspective_requested)`
- Ensures consistency for same community-topic pairs
- Update cache periodically to reflect evolving views

**Controversy Detection:**
- Initial: Rule-based classifier with hand-labeled controversial topics
- Future: ML classifier trained on engagement data

**How to select "community":**

HARD-CODED tier system:
```
├─> Tier 1: Major world religions (Christianity, Islam, Hinduism, Buddhism, Judaism, Sikhism, secular/atheist)
├─> Tier 2: Political orientations (progressive, conservative, libertarian, socialist)
├─> Tier 3: Regional/cultural (Global North/South, specific regions on demand)
└─> Tier 4: Professional/expertise (scientists, ethicists, legal scholars)
```

MODEL-CHOSEN refinement:
```
├─> Within each tier, select WHICH specific communities based on query relevance
├─> Choose appropriate sub-communities (e.g., Sunni vs Shia, Catholic vs Protestant)
└─> Determine weighting/prominence based on controversy intensity
```

- Hard-code when: Ensuring representation fairness, avoiding systematic exclusion
- Model-choose when: Query-specific relevance, sub-community selection, weighting

**Common Knowledge Scope:**

*Primary: WITHIN-community common knowledge*
- Goal: Help users understand what others in their community believe
- Reduces pluralistic ignorance within groups
- Example: "Many progressive Christians support LGBTQ+ rights" shown to progressive Christian user

*Secondary: ACROSS-community common knowledge (optional for MVP)*
- Goal: Help users understand what other communities actually believe
- Reduces outgroup homogeneity bias
- Example: "Most Muslims condemn terrorism" shown to non-Muslim users

## MVP Scoping

### Must-Haves (MVP v1)

**Core Functionality:**
- [ ] Basic survey (10-12 questions) to infer communities
- [ ] Hard-coded Tier 1 communities (major religions, political orientations)
- [ ] Controversy detection: Works for religious + political cleavages only
- [ ] Perspective surfacing: Shows user's community + 1-2 others
- [ ] Consistency: Same model call for same community-topic pair (caching)
- [ ] Explicit framing: "Perspectives from [community]" labels

**Evaluation:**
- [ ] Consistency score automated pipeline
- [ ] Coverage score for 20 hand-labeled test queries
- [ ] Representation accuracy tested with 20 community members (4 communities x 5 people)

**Scope Limits:**
- Single language (English)
- Text-only responses
- No personalization beyond community membership
- No cross-community common knowledge (within-community only)
- No dynamic community discovery (hard-coded list only)

### Should-Haves (MVP v2)

- [ ] Model-chosen sub-community selection within hard-coded tiers
- [ ] Regional/cultural communities (Tier 3)
- [ ] Appropriateness classifier (when to surface perspectives)
- [ ] Basic fairness evaluation (Tier 2 #5)
- [ ] User feedback mechanism ("Was this perspective accurate?")

### Nice-to-Haves (Future)

- [ ] Cross-community common knowledge
- [ ] Dynamic community discovery
- [ ] Multi-lingual support
- [ ] Longitudinal tracking of belief updates
- [ ] Full Pinker-style evaluation
- [ ] Professional/expertise communities (Tier 4)
