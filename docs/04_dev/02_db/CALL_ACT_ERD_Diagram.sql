CREATE TYPE "consultation_status" AS ENUM (
  'completed',
  'in_progress',
  'incomplete'
);

CREATE TYPE "card_type" AS ENUM (
  'credit',
  'debit'
);

CREATE TYPE "brand_type" AS ENUM (
  'visa',
  'mastercard',
  'amex',
  'unionpay',
  'local'
);

CREATE TYPE "consultation_category" AS ENUM (
  'card_loss',
  'overseas_payment',
  'fee_inquiry',
  'points',
  'limit_inquiry',
  'other'
);

CREATE TYPE "benefit_type" AS ENUM (
  'discount',
  'points_accrual',
  'cashback'
);

CREATE TYPE "fee_type" AS ENUM (
  'overseas_fee',
  'cash_service_fee',
  'annual_fee'
);

CREATE TYPE "emotion_type" AS ENUM (
  'positive',
  'neutral',
  'negative'
);

CREATE TYPE "quality_rating" AS ENUM (
  'high',
  'medium',
  'low'
);

CREATE TYPE "speaker_type" AS ENUM (
  'customer',
  'agent'
);

CREATE TYPE "difficulty_level" AS ENUM (
  'beginner',
  'intermediate',
  'advanced'
);

CREATE TYPE "scenario_type" AS ENUM (
  'real_case',
  'llm_generated'
);

CREATE TYPE "notice_priority" AS ENUM (
  'normal',
  'important',
  'urgent'
);

CREATE TYPE "notice_category" AS ENUM (
  'system',
  'service',
  'emergency'
);

CREATE TYPE "status" AS ENUM (
  'active',
  'inactive',
  'suspended'
);

CREATE TYPE "promotion_status" AS ENUM (
  'ongoing',
  'ended'
);

CREATE TYPE "card_status" AS ENUM (
  'active',
  'suspended',
  'lost',
  'terminated'
);

CREATE TABLE "card_products" (
  "id" varchar(50) PRIMARY KEY,
  "name" varchar(200) NOT NULL,
  "card_type" card_type NOT NULL,
  "brand" brand_type,
  "annual_fee_domestic" int,
  "annual_fee_global" int,
  "performance_condition" text,
  "main_benefits" text,
  "status" status DEFAULT 'active',
  "metadata" jsonb,
  "structured" jsonb,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "card_benefits" (
  "id" serial PRIMARY KEY,
  "card_id" varchar(50) NOT NULL,
  "category" varchar(100),
  "benefit_type" benefit_type NOT NULL,
  "benefit_rate" decimal(5,2),
  "benefit_limit" int,
  "condition_text" text,
  "partner_name" varchar(200),
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "fee_info" (
  "id" serial PRIMARY KEY,
  "fee_type" fee_type NOT NULL,
  "card_id" varchar(50),
  "fee_rate" decimal(5,2),
  "fixed_fee" int,
  "description" text,
  "exemption_condition" text,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "point_policy" (
  "id" serial PRIMARY KEY,
  "card_id" varchar(50) NOT NULL,
  "category" varchar(100),
  "point_rate" decimal(5,2),
  "point_unit" int,
  "expiry_months" int,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "promotions" (
  "id" varchar(50) PRIMARY KEY,
  "title" varchar(200) NOT NULL,
  "card_id" varchar(50),
  "start_date" date NOT NULL,
  "end_date" date NOT NULL,
  "benefit_description" text,
  "conditions" text,
  "target_customer" varchar(50),
  "status" promotion_status DEFAULT 'ongoing',
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "customer_cards" (
  "id" serial PRIMARY KEY,
  "customer_id" varchar(50) NOT NULL,
  "card_id" varchar(50) NOT NULL,
  "issued_date" date NOT NULL,
  "card_number_hash" varchar(64),
  "card_status" card_status DEFAULT 'active',
  "is_primary" boolean DEFAULT false,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "notices" (
  "id" varchar(50) PRIMARY KEY,
  "title" varchar(300) NOT NULL,
  "content" text NOT NULL,
  "category" notice_category NOT NULL,
  "priority" notice_priority DEFAULT 'normal',
  "is_pinned" boolean DEFAULT false,
  "start_date" date NOT NULL,
  "end_date" date,
  "status" status DEFAULT 'active',
  "created_by" varchar(50),
  "keywords" text[],
  "embedding" vector(1536),
  "metadata" jsonb,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "frequent_inquiries" (
  "id" serial PRIMARY KEY,
  "category" consultation_category NOT NULL,
  "question" text NOT NULL,
  "answer" text NOT NULL,
  "view_count" int DEFAULT 0,
  "is_active" boolean DEFAULT true,
  "display_order" int,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "inquiry_view_log" (
  "id" serial PRIMARY KEY,
  "inquiry_id" int NOT NULL,
  "viewed_by" varchar(50),
  "viewed_at" timestamp DEFAULT (now())
);

CREATE TABLE "service_guide_documents" (
  "id" varchar(100) PRIMARY KEY,
  "document_type" varchar(50),
  "category" varchar(100),
  "title" varchar(300) NOT NULL,
  "content" text NOT NULL,
  "keywords" text[],
  "embedding" vector(1536),
  "metadata" jsonb,
  "document_source" varchar(200),
  "priority" varchar(20) DEFAULT 'normal',
  "usage_count" int DEFAULT 0,
  "last_used" timestamp,
  "structured" jsonb,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "employees" (
  "id" varchar(50) PRIMARY KEY,
  "name" varchar(100) NOT NULL,
  "email" varchar(100) UNIQUE,
  "role" varchar(50),
  "department" varchar(100),
  "hire_date" date,
  "status" status DEFAULT 'active',
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "consultations" (
  "id" varchar(50) PRIMARY KEY,
  "customer_id" varchar(50) NOT NULL,
  "agent_id" varchar(50) NOT NULL,
  "status" consultation_status DEFAULT 'in_progress',
  "category" consultation_category NOT NULL,
  "title" text,
  "call_date" date NOT NULL,
  "call_time" time NOT NULL,
  "call_duration" varchar(20),
  "fcr" boolean,
  "is_best_practice" boolean DEFAULT false,
  "quality_score" int,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "consultation_transcripts" (
  "id" serial PRIMARY KEY,
  "consultation_id" varchar(50) NOT NULL,
  "speaker" speaker_type NOT NULL,
  "message" text NOT NULL,
  "timestamp" time NOT NULL,
  "sentiment" emotion_type,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "consultation_summaries" (
  "id" serial PRIMARY KEY,
  "consultation_id" varchar(50) UNIQUE NOT NULL,
  "ai_summary" text,
  "memo" text,
  "follow_up_tasks" text,
  "handoff_department" varchar(100),
  "handoff_notes" text,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "consultation_feedback" (
  "id" serial PRIMARY KEY,
  "consultation_id" varchar(50) UNIQUE NOT NULL,
  "emotion_start" emotion_type,
  "emotion_middle" emotion_type,
  "emotion_end" emotion_type,
  "quality_score" quality_rating,
  "processing_time_score" int,
  "gratitude_score" int,
  "emotion_shift_score" int,
  "manual_compliance_score" int,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "stt_keywords" (
  "id" serial PRIMARY KEY,
  "consultation_id" varchar(50) NOT NULL,
  "keyword" varchar(100) NOT NULL,
  "confidence" float,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "training_scenarios" (
  "id" varchar(50) PRIMARY KEY,
  "title" varchar(200) NOT NULL,
  "description" text,
  "difficulty" difficulty_level NOT NULL,
  "estimated_duration" varchar(20),
  "category" consultation_category NOT NULL,
  "tags" text[],
  "scenario_type" scenario_type NOT NULL,
  "source_consultation_id" varchar(50),
  "is_locked" boolean DEFAULT false,
  "unlock_condition" text,
  "pass_score" int DEFAULT 80,
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp
);

CREATE TABLE "scenario_scripts" (
  "id" serial PRIMARY KEY,
  "scenario_id" varchar(50) NOT NULL,
  "step_order" int NOT NULL,
  "speaker" speaker_type NOT NULL,
  "message" text,
  "expected_keywords" text[],
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "scenario_evaluation_criteria" (
  "id" serial PRIMARY KEY,
  "scenario_id" varchar(50) NOT NULL,
  "criteria_name" varchar(200) NOT NULL,
  "max_score" int NOT NULL,
  "keywords" text[],
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "scenario_attempts" (
  "id" serial PRIMARY KEY,
  "scenario_id" varchar(50) NOT NULL,
  "agent_id" varchar(50) NOT NULL,
  "score" int,
  "duration" varchar(20),
  "completed_at" timestamp NOT NULL,
  "evaluation_detail" jsonb,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "best_practices" (
  "id" serial PRIMARY KEY,
  "consultation_id" varchar(50) UNIQUE NOT NULL,
  "title" varchar(200) NOT NULL,
  "category" consultation_category NOT NULL,
  "key_takeaway" text,
  "recommended_for" text[],
  "views" int DEFAULT 0,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "consultation_documents" (
  "id" varchar(50) PRIMARY KEY,
  "consultation_id" varchar(50),
  "document_type" varchar(50),
  "category" consultation_category NOT NULL,
  "title" varchar(300) NOT NULL,
  "content" text NOT NULL,
  "keywords" text[],
  "embedding" vector(1536),
  "metadata" jsonb,
  "usage_count" int DEFAULT 0,
  "effectiveness_score" decimal(3,2),
  "last_used" timestamp,
  "created_at" timestamp DEFAULT (now())
);

CREATE INDEX ON "card_benefits" ("card_id");

CREATE INDEX ON "card_benefits" ("category");

CREATE INDEX ON "card_benefits" ("benefit_type");

CREATE INDEX ON "fee_info" ("card_id");

CREATE INDEX ON "fee_info" ("fee_type");

CREATE INDEX ON "point_policy" ("card_id");

CREATE INDEX ON "promotions" ("card_id");

CREATE INDEX ON "promotions" ("start_date", "end_date");

CREATE INDEX ON "promotions" ("status");

CREATE INDEX ON "customer_cards" ("customer_id");

CREATE INDEX ON "customer_cards" ("card_id");

CREATE UNIQUE INDEX ON "customer_cards" ("customer_id", "card_id");

CREATE INDEX ON "notices" ("category");

CREATE INDEX ON "notices" ("priority");

CREATE INDEX ON "notices" ("is_pinned");

CREATE INDEX ON "notices" ("start_date", "end_date");

CREATE INDEX "idx_notices_embedding_hnsw" ON "notices" USING hnsw ("embedding" vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX ON "frequent_inquiries" ("category");

CREATE INDEX ON "frequent_inquiries" ("display_order");

CREATE INDEX ON "frequent_inquiries" ("view_count");

CREATE INDEX ON "inquiry_view_log" ("inquiry_id");

CREATE INDEX ON "inquiry_view_log" ("viewed_by");

CREATE INDEX ON "inquiry_view_log" ("viewed_at");

CREATE INDEX ON "service_guide_documents" ("document_type");

CREATE INDEX ON "service_guide_documents" ("category");

CREATE INDEX ON "service_guide_documents" ("usage_count");

CREATE INDEX ON "employees" ("role");

CREATE INDEX ON "employees" ("department");

CREATE INDEX ON "employees" ("status");

CREATE INDEX ON "consultations" ("customer_id");

CREATE INDEX ON "consultations" ("agent_id");

CREATE INDEX ON "consultations" ("status");

CREATE INDEX ON "consultations" ("category");

CREATE INDEX ON "consultations" ("call_date");

CREATE INDEX ON "consultations" ("fcr");

CREATE INDEX ON "consultations" ("is_best_practice");

CREATE INDEX ON "consultation_transcripts" ("consultation_id");

CREATE INDEX ON "consultation_transcripts" ("speaker");

CREATE INDEX ON "consultation_transcripts" ("timestamp");

CREATE INDEX ON "consultation_summaries" ("consultation_id");

CREATE INDEX ON "consultation_feedback" ("consultation_id");

CREATE INDEX ON "stt_keywords" ("consultation_id");

CREATE INDEX ON "stt_keywords" ("keyword");

CREATE INDEX ON "training_scenarios" ("difficulty");

CREATE INDEX ON "training_scenarios" ("category");

CREATE INDEX ON "training_scenarios" ("scenario_type");

CREATE INDEX ON "training_scenarios" ("is_locked");

CREATE INDEX ON "scenario_scripts" ("scenario_id");

CREATE INDEX ON "scenario_scripts" ("step_order");

CREATE INDEX ON "scenario_evaluation_criteria" ("scenario_id");

CREATE INDEX ON "scenario_attempts" ("scenario_id");

CREATE INDEX ON "scenario_attempts" ("agent_id");

CREATE INDEX ON "scenario_attempts" ("completed_at");

CREATE INDEX ON "scenario_attempts" ("score");

CREATE INDEX ON "best_practices" ("consultation_id");

CREATE INDEX ON "best_practices" ("category");

CREATE INDEX ON "best_practices" ("views");

CREATE INDEX ON "consultation_documents" ("consultation_id");

CREATE INDEX ON "consultation_documents" ("document_type");

CREATE INDEX ON "consultation_documents" ("category");

CREATE INDEX ON "consultation_documents" ("usage_count");

COMMENT ON TABLE "card_products" IS '카드 상품 마스터 테이블';

COMMENT ON COLUMN "card_products"."id" IS 'CARD-001';

COMMENT ON COLUMN "card_products"."name" IS '하나카드 원큐 VIVA 체크카드';

COMMENT ON COLUMN "card_products"."annual_fee_domestic" IS '국내전용 연회비';

COMMENT ON COLUMN "card_products"."annual_fee_global" IS '해외겸용 연회비';

COMMENT ON COLUMN "card_products"."performance_condition" IS '실적 조건';

COMMENT ON COLUMN "card_products"."main_benefits" IS '주요 혜택 (간략)';

COMMENT ON COLUMN "card_products"."metadata" IS '추가 메타데이터 (original_source, full_content 등)';

COMMENT ON COLUMN "card_products"."structured" IS 'RAG 검색용 구조화 데이터 (프론트엔드 표시용)';

COMMENT ON TABLE "card_benefits" IS '카드 혜택 상세 테이블';

COMMENT ON COLUMN "card_benefits"."category" IS '주유, 커피, 편의점, 통신비';

COMMENT ON COLUMN "card_benefits"."benefit_rate" IS '5.00 = 5% 할인';

COMMENT ON COLUMN "card_benefits"."benefit_limit" IS '월 한도 (원)';

COMMENT ON COLUMN "card_benefits"."condition_text" IS '월 30만원 이상 이용시';

COMMENT ON COLUMN "card_benefits"."partner_name" IS '제휴사명 (SK에너지, 스타벅스 등)';

COMMENT ON TABLE "fee_info" IS '수수료 정보 테이블';

COMMENT ON COLUMN "fee_info"."fee_rate" IS '1.50 = 1.5%';

COMMENT ON COLUMN "fee_info"."fixed_fee" IS '고정 수수료 (원)';

COMMENT ON COLUMN "fee_info"."exemption_condition" IS '면제 조건';

COMMENT ON TABLE "point_policy" IS '포인트 정책 테이블';

COMMENT ON COLUMN "point_policy"."category" IS '일반가맹점, 해외가맹점';

COMMENT ON COLUMN "point_policy"."point_rate" IS '0.50 = 0.5% 적립';

COMMENT ON COLUMN "point_policy"."point_unit" IS '적립 단위 (1000원당)';

COMMENT ON COLUMN "point_policy"."expiry_months" IS '포인트 유효기간 (개월)';

COMMENT ON TABLE "promotions" IS '프로모션 정보 테이블';

COMMENT ON COLUMN "promotions"."id" IS 'PROMO-2025-001';

COMMENT ON COLUMN "promotions"."title" IS '하나카드x메가커피 프로모션';

COMMENT ON COLUMN "promotions"."target_customer" IS '신규고객, 전체, 우수고객';

COMMENT ON TABLE "customer_cards" IS '고객-카드 연결 테이블 (customer_id는 외부 시스템 참조)';

COMMENT ON COLUMN "customer_cards"."customer_id" IS '외부 시스템 고객 ID (FK 없음)';

COMMENT ON COLUMN "customer_cards"."issued_date" IS '발급일';

COMMENT ON COLUMN "customer_cards"."card_number_hash" IS '카드번호 해시 (보안)';

COMMENT ON COLUMN "customer_cards"."is_primary" IS '주 카드 여부';

COMMENT ON TABLE "notices" IS '공지사항 테이블';

COMMENT ON COLUMN "notices"."id" IS 'NOTICE-2025-001';

COMMENT ON COLUMN "notices"."keywords" IS 'RAG 검색용 키워드 배열';

COMMENT ON COLUMN "notices"."embedding" IS 'RAG 검색용 벡터 임베딩 (OpenAI embedding)';

COMMENT ON COLUMN "notices"."metadata" IS '추가 메타데이터 (original_source 등)';

COMMENT ON COLUMN "notices"."is_pinned" IS '상단 고정 여부';

COMMENT ON COLUMN "notices"."created_by" IS '작성자 ID';

COMMENT ON COLUMN "notices"."keywords" IS 'RAG 검색용 키워드 배열';

COMMENT ON COLUMN "notices"."embedding" IS 'RAG 검색용 벡터 임베딩 (OpenAI embedding)';

COMMENT ON COLUMN "notices"."metadata" IS '추가 메타데이터 (original_source 등)';

COMMENT ON TABLE "frequent_inquiries" IS '자주 찾는 문의 테이블';

COMMENT ON COLUMN "frequent_inquiries"."question" IS '연회비는 언제 청구되나요?';

COMMENT ON COLUMN "frequent_inquiries"."answer" IS '카드 발급일 기준 1년 후...';

COMMENT ON COLUMN "frequent_inquiries"."view_count" IS '조회수';

COMMENT ON COLUMN "frequent_inquiries"."display_order" IS '표시 순서';

COMMENT ON TABLE "inquiry_view_log" IS '문의 조회 로그 테이블';

COMMENT ON COLUMN "inquiry_view_log"."viewed_by" IS '조회한 사용자 ID';

COMMENT ON TABLE "service_guide_documents" IS '카드사 이용 안내 문서 + VectorDB 메타데이터';

COMMENT ON COLUMN "service_guide_documents"."id" IS 'DOC-GUIDE-001';

COMMENT ON COLUMN "service_guide_documents"."document_type" IS 'usage_guide, consumer_alert, financial_guide';

COMMENT ON COLUMN "service_guide_documents"."category" IS '신용카드사용가이드, 소비자주의경보';

COMMENT ON COLUMN "service_guide_documents"."keywords" IS '검색 키워드 배열';

COMMENT ON COLUMN "service_guide_documents"."embedding" IS 'OpenAI embedding vector for RAG';

COMMENT ON COLUMN "service_guide_documents"."metadata" IS '추가 메타데이터 (JSON)';

COMMENT ON COLUMN "service_guide_documents"."document_source" IS '출처: 금융감독원 가이드라인';

COMMENT ON COLUMN "service_guide_documents"."structured" IS 'RAG 검색용 구조화 데이터 (프론트엔드 Kanban board 표시용)';

COMMENT ON COLUMN "service_guide_documents"."structured" IS 'RAG 검색용 구조화 데이터 (프론트엔드 Kanban board 표시용)';

COMMENT ON TABLE "employees" IS '직원(상담사) 정보 테이블';

COMMENT ON COLUMN "employees"."id" IS 'EMP-001';

COMMENT ON COLUMN "employees"."role" IS '상담사, 매니저, 관리자';

COMMENT ON COLUMN "employees"."department" IS '상담팀, 카드발급팀';

COMMENT ON TABLE "consultations" IS '상담 마스터 테이블 (customer_id는 외부 시스템 참조)';

COMMENT ON COLUMN "consultations"."id" IS 'CS-20250105-1432';

COMMENT ON COLUMN "consultations"."customer_id" IS '외부 시스템 고객 ID (FK 없음)';

COMMENT ON COLUMN "consultations"."title" IS '카드 분실 신고 및 재발급 요청';

COMMENT ON COLUMN "consultations"."call_duration" IS '5:23';

COMMENT ON COLUMN "consultations"."fcr" IS 'First Call Resolution';

COMMENT ON COLUMN "consultations"."is_best_practice" IS '우수 사례 여부';

COMMENT ON COLUMN "consultations"."quality_score" IS '품질 점수 (0-100)';

COMMENT ON TABLE "consultation_transcripts" IS '상담 전문 (STT 결과) 테이블';

COMMENT ON COLUMN "consultation_transcripts"."sentiment" IS '감정 분석 결과';

COMMENT ON TABLE "consultation_summaries" IS '상담 요약 및 후처리 테이블';

COMMENT ON COLUMN "consultation_summaries"."ai_summary" IS 'AI가 생성한 요약';

COMMENT ON COLUMN "consultation_summaries"."memo" IS '상담사 메모';

COMMENT ON COLUMN "consultation_summaries"."follow_up_tasks" IS '후속 일정';

COMMENT ON COLUMN "consultation_summaries"."handoff_department" IS '이관 부서';

COMMENT ON COLUMN "consultation_summaries"."handoff_notes" IS '이관 사항';

COMMENT ON TABLE "consultation_feedback" IS '감정 분석 및 피드백 테이블';

COMMENT ON COLUMN "consultation_feedback"."emotion_start" IS '초반 감정';

COMMENT ON COLUMN "consultation_feedback"."emotion_middle" IS '중반 감정';

COMMENT ON COLUMN "consultation_feedback"."emotion_end" IS '후반 감정';

COMMENT ON COLUMN "consultation_feedback"."quality_score" IS '품질 평가: 상/중/하';

COMMENT ON COLUMN "consultation_feedback"."processing_time_score" IS '후처리 소요 시간 점수 (0-100)';

COMMENT ON COLUMN "consultation_feedback"."gratitude_score" IS '감사 표현 비율 점수';

COMMENT ON COLUMN "consultation_feedback"."emotion_shift_score" IS '감정 전환 점수';

COMMENT ON COLUMN "consultation_feedback"."manual_compliance_score" IS '매뉴얼 준수 점수';

COMMENT ON TABLE "stt_keywords" IS 'STT 키워드 추출 테이블';

COMMENT ON COLUMN "stt_keywords"."keyword" IS '카드분실, 해외결제';

COMMENT ON COLUMN "stt_keywords"."confidence" IS '신뢰도 (0-1)';

COMMENT ON TABLE "training_scenarios" IS '교육 시나리오 테이블';

COMMENT ON COLUMN "training_scenarios"."id" IS 'SIM-001';

COMMENT ON COLUMN "training_scenarios"."title" IS '카드 분실 신고 및 재발급';

COMMENT ON COLUMN "training_scenarios"."description" IS '시나리오 설명';

COMMENT ON COLUMN "training_scenarios"."estimated_duration" IS '5분, 10분';

COMMENT ON COLUMN "training_scenarios"."tags" IS '검색 태그 배열';

COMMENT ON COLUMN "training_scenarios"."source_consultation_id" IS '실제 사례 기반인 경우 원본 상담 ID';

COMMENT ON COLUMN "training_scenarios"."is_locked" IS '잠금 여부';

COMMENT ON COLUMN "training_scenarios"."unlock_condition" IS '잠금 해제 조건';

COMMENT ON COLUMN "training_scenarios"."pass_score" IS '합격 점수';

COMMENT ON TABLE "scenario_scripts" IS '시나리오 대화 스크립트 테이블';

COMMENT ON COLUMN "scenario_scripts"."step_order" IS '대화 순서';

COMMENT ON COLUMN "scenario_scripts"."message" IS '대화 내용 (상담사는 null)';

COMMENT ON COLUMN "scenario_scripts"."expected_keywords" IS '상담사가 말해야 할 키워드 (평가용)';

COMMENT ON TABLE "scenario_evaluation_criteria" IS '시나리오 평가 기준 테이블';

COMMENT ON COLUMN "scenario_evaluation_criteria"."criteria_name" IS '고객 인사, 분실 확인, 재발급 안내';

COMMENT ON COLUMN "scenario_evaluation_criteria"."max_score" IS '최대 점수';

COMMENT ON COLUMN "scenario_evaluation_criteria"."keywords" IS '필수 키워드';

COMMENT ON TABLE "scenario_attempts" IS '시나리오 시도 기록 테이블';

COMMENT ON COLUMN "scenario_attempts"."score" IS '획득 점수';

COMMENT ON COLUMN "scenario_attempts"."duration" IS '소요 시간';

COMMENT ON COLUMN "scenario_attempts"."evaluation_detail" IS '평가 상세 내역 (JSON)';

COMMENT ON TABLE "best_practices" IS '우수 상담 사례 테이블';

COMMENT ON COLUMN "best_practices"."title" IS '진상 고객 대응 우수 사례';

COMMENT ON COLUMN "best_practices"."key_takeaway" IS '핵심 포인트';

COMMENT ON COLUMN "best_practices"."recommended_for" IS '추천 대상: 신입, 중급';

COMMENT ON COLUMN "best_practices"."views" IS '조회수';

COMMENT ON TABLE "consultation_documents" IS '상담 사례 문서 + VectorDB 메타데이터 테이블';

COMMENT ON COLUMN "consultation_documents"."id" IS 'DOC-CONSULT-001';

COMMENT ON COLUMN "consultation_documents"."document_type" IS 'past_consultation, training_scenario';

COMMENT ON COLUMN "consultation_documents"."content" IS '상담 요약 또는 시나리오 내용';

COMMENT ON COLUMN "consultation_documents"."keywords" IS '검색 키워드 배열';

COMMENT ON COLUMN "consultation_documents"."embedding" IS 'OpenAI embedding vector for RAG';

COMMENT ON COLUMN "consultation_documents"."metadata" IS '추가 메타데이터 (agent_id, fcr, quality_score 등)';

COMMENT ON COLUMN "consultation_documents"."effectiveness_score" IS '효과성 점수 (0-1)';

ALTER TABLE "card_benefits" ADD FOREIGN KEY ("card_id") REFERENCES "card_products" ("id");

ALTER TABLE "fee_info" ADD FOREIGN KEY ("card_id") REFERENCES "card_products" ("id");

ALTER TABLE "point_policy" ADD FOREIGN KEY ("card_id") REFERENCES "card_products" ("id");

ALTER TABLE "promotions" ADD FOREIGN KEY ("card_id") REFERENCES "card_products" ("id");

ALTER TABLE "customer_cards" ADD FOREIGN KEY ("card_id") REFERENCES "card_products" ("id");

ALTER TABLE "inquiry_view_log" ADD FOREIGN KEY ("inquiry_id") REFERENCES "frequent_inquiries" ("id");

ALTER TABLE "consultations" ADD FOREIGN KEY ("agent_id") REFERENCES "employees" ("id");

ALTER TABLE "consultation_transcripts" ADD FOREIGN KEY ("consultation_id") REFERENCES "consultations" ("id");

ALTER TABLE "consultation_summaries" ADD FOREIGN KEY ("consultation_id") REFERENCES "consultations" ("id");

ALTER TABLE "consultation_feedback" ADD FOREIGN KEY ("consultation_id") REFERENCES "consultations" ("id");

ALTER TABLE "stt_keywords" ADD FOREIGN KEY ("consultation_id") REFERENCES "consultations" ("id");

ALTER TABLE "training_scenarios" ADD FOREIGN KEY ("source_consultation_id") REFERENCES "consultations" ("id");

ALTER TABLE "scenario_scripts" ADD FOREIGN KEY ("scenario_id") REFERENCES "training_scenarios" ("id");

ALTER TABLE "scenario_evaluation_criteria" ADD FOREIGN KEY ("scenario_id") REFERENCES "training_scenarios" ("id");

ALTER TABLE "scenario_attempts" ADD FOREIGN KEY ("scenario_id") REFERENCES "training_scenarios" ("id");

ALTER TABLE "scenario_attempts" ADD FOREIGN KEY ("agent_id") REFERENCES "employees" ("id");

ALTER TABLE "best_practices" ADD FOREIGN KEY ("consultation_id") REFERENCES "consultations" ("id");

ALTER TABLE "consultation_documents" ADD FOREIGN KEY ("consultation_id") REFERENCES "consultations" ("id");
