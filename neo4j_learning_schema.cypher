// ===========================================================================
// Neo4j Learning Schema for Horizon + LuciCRM
// 
// Shared schema for storing system learnings from user feedback.
// Both applications use ctx-engineering-py for session/memory management,
// with this graph schema for persistent learning storage.
// ===========================================================================

// ---------------------------------------------------------------------------
// CONSTRAINTS (Run once to set up)
// ---------------------------------------------------------------------------

// Learning nodes - unique IDs
CREATE CONSTRAINT learning_id IF NOT EXISTS FOR (l:Learning) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT feedback_id IF NOT EXISTS FOR (f:Feedback) REQUIRE f.id IS UNIQUE;

// Application-specific nodes
CREATE CONSTRAINT article_memory_id IF NOT EXISTS FOR (a:ArticleMemory) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT contact_preference_id IF NOT EXISTS FOR (c:ContactPreference) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT message_pattern_id IF NOT EXISTS FOR (m:MessagePattern) REQUIRE m.id IS UNIQUE;

// Indexes for common queries
CREATE INDEX learning_scope_idx IF NOT EXISTS FOR (l:Learning) ON (l.scope, l.owner_id);
CREATE INDEX learning_app_idx IF NOT EXISTS FOR (l:Learning) ON (l.app);
CREATE INDEX learning_created_idx IF NOT EXISTS FOR (l:Learning) ON (l.created_at);
CREATE INDEX pattern_type_idx IF NOT EXISTS FOR (p:Pattern) ON (p.pattern_type);
CREATE INDEX feedback_session_idx IF NOT EXISTS FOR (f:Feedback) ON (f.session_id);

// ---------------------------------------------------------------------------
// LEARNING NODE TYPES (Shared across apps)
// ---------------------------------------------------------------------------

// Base Learning node - abstract pattern that both apps derive from
// Properties:
//   - id: unique identifier
//   - scope: 'user' | 'session' | 'app'
//   - owner_id: user_id for user scope, session_id for session scope, null for app
//   - app: 'horizon' | 'lucicrm'
//   - content: JSON string with learning content
//   - importance: 0.0-1.0 importance score
//   - confidence: 0.0-1.0 confidence score
//   - source_session_id: session that produced this learning
//   - created_at: timestamp
//   - updated_at: timestamp
//   - expires_at: optional expiry timestamp
//   - access_count: how often this learning has been retrieved
//   - last_accessed_at: when it was last used

// Example Learning creation:
// CREATE (l:Learning {
//   id: 'learn-abc123',
//   scope: 'user',
//   owner_id: 'richard',
//   app: 'horizon',
//   content: '{"type": "tone_preference", "value": "contrarian_but_evidence_based"}',
//   importance: 0.8,
//   confidence: 0.9,
//   source_session_id: 'session-xyz',
//   created_at: datetime(),
//   updated_at: datetime(),
//   access_count: 0
// })

// ---------------------------------------------------------------------------
// HORIZON-SPECIFIC NODE TYPES
// ---------------------------------------------------------------------------

// ArticleMemory - Learnings from article generation/feedback
// Extends Learning with article-specific fields
// Example:
// CREATE (a:ArticleMemory:Learning {
//   id: 'artmem-abc123',
//   scope: 'app',
//   app: 'horizon',
//   memory_type: 'successful_pattern',  // 'successful_pattern' | 'rejected_approach' | 'style_preference'
//   topic_domain: 'monetary_policy',
//   content: '{"pattern": "Start with market expectations vs consensus", "success_rate": 0.85}',
//   importance: 0.75,
//   confidence: 0.8,
//   created_at: datetime()
// })

// ToneCalibration - User's preferred writing tone
// CREATE (t:ToneCalibration:Learning {
//   id: 'tone-abc123',
//   scope: 'user',
//   owner_id: 'richard',
//   app: 'horizon',
//   dimension: 'formality',  // 'formality' | 'technicality' | 'contrarian_level' | 'data_density'
//   preferred_value: 0.7,  // 0.0-1.0 scale
//   examples: '["Use active voice", "Lead with data"]',
//   created_at: datetime()
// })

// TopicKnowledge - Domain-specific facts learned
// CREATE (k:TopicKnowledge:Learning {
//   id: 'topic-abc123',
//   scope: 'app',
//   app: 'horizon',
//   topic: 'federal_reserve',
//   fact_type: 'relationship',  // 'relationship' | 'precedent' | 'market_reaction'
//   content: '{"fact": "Markets typically price in FOMC decisions 48h before", "confidence": 0.9}',
//   created_at: datetime()
// })

// ---------------------------------------------------------------------------
// LUCICRM-SPECIFIC NODE TYPES
// ---------------------------------------------------------------------------

// ContactPreference - Per-contact communication preferences
// CREATE (c:ContactPreference:Learning {
//   id: 'cpref-abc123',
//   scope: 'user',  // scope is always 'user' but owner_id is the contact
//   owner_id: 'contact-12345',
//   app: 'lucicrm',
//   preference_type: 'tone',  // 'tone' | 'length' | 'topics' | 'frequency'
//   content: '{"prefers": "concise", "avoid": "jargon", "interests": ["AI", "derivatives"]}',
//   importance: 0.8,
//   confidence: 0.7,
//   created_at: datetime()
// })

// MessagePattern - Successful outreach patterns
// CREATE (m:MessagePattern:Learning {
//   id: 'msgpat-abc123',
//   scope: 'app',
//   app: 'lucicrm',
//   pattern_type: 'opening',  // 'opening' | 'call_to_action' | 'value_hook' | 'subject_line'
//   target_persona: 'hedge_fund_cio',
//   content: '{"pattern": "Reference recent market event + personal insight", "response_rate": 0.45}',
//   importance: 0.85,
//   confidence: 0.75,
//   created_at: datetime()
// })

// EngagementSignal - Response/engagement tracking
// CREATE (e:EngagementSignal:Learning {
//   id: 'engage-abc123',
//   scope: 'user',
//   owner_id: 'contact-12345',
//   app: 'lucicrm',
//   signal_type: 'reply',  // 'reply' | 'click' | 'open' | 'meeting_booked'
//   message_id: 'msg-xyz',
//   context: '{"topic": "ECB preview", "sent_at": "2026-02-10T09:00:00Z"}',
//   created_at: datetime()
// })

// ---------------------------------------------------------------------------
// RELATIONSHIPS
// ---------------------------------------------------------------------------

// Learning relationships
// (Learning)-[:DERIVED_FROM]->(Session)
// (Learning)-[:SUPERSEDES]->(Learning)  // newer learning replacing older
// (Learning)-[:CONTRADICTS]->(Learning) // conflicting learnings
// (Learning)-[:SUPPORTS]->(Learning)    // reinforcing learnings

// Horizon relationships
// (ArticleMemory)-[:ABOUT_TOPIC]->(Topic)
// (ArticleMemory)-[:FROM_ARTICLE]->(Article)
// (ToneCalibration)-[:APPLIES_TO]->(Topic)

// LuciCRM relationships
// (ContactPreference)-[:FOR_CONTACT]->(Contact)
// (MessagePattern)-[:EFFECTIVE_FOR]->(Persona)
// (EngagementSignal)-[:FROM_MESSAGE]->(Message)

// ---------------------------------------------------------------------------
// EXAMPLE QUERIES
// ---------------------------------------------------------------------------

// Get all learnings for Horizon article generation (user + app scope)
// MATCH (l:Learning)
// WHERE l.app = 'horizon'
//   AND (l.scope = 'app' OR (l.scope = 'user' AND l.owner_id = $user_id))
// RETURN l
// ORDER BY l.importance DESC, l.updated_at DESC
// LIMIT 20

// Get contact preferences for email composition
// MATCH (c:ContactPreference)
// WHERE c.owner_id = $contact_id
// RETURN c
// ORDER BY c.importance DESC

// Get successful message patterns for a persona
// MATCH (m:MessagePattern)
// WHERE m.target_persona = $persona_type
//   AND m.confidence > 0.6
// RETURN m
// ORDER BY m.importance DESC
// LIMIT 10

// Multi-signal retrieval (relevance + recency + importance)
// This would typically be done in application code combining:
// 1. Vector similarity search for relevance
// 2. Time decay function for recency
// 3. importance field for importance score

// ---------------------------------------------------------------------------
// INITIALIZATION (Run once per database)
// ---------------------------------------------------------------------------

// Create app-level configuration nodes
MERGE (h:AppConfig {app: 'horizon'})
SET h.version = '1.0',
    h.last_schema_update = datetime(),
    h.learning_extraction_model = 'claude-opus-4-5';

MERGE (c:AppConfig {app: 'lucicrm'})
SET c.version = '1.0',
    c.last_schema_update = datetime(),
    c.learning_extraction_model = 'claude-opus-4-5';
