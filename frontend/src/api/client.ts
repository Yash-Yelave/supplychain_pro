import axios from 'axios';

// Use VITE_API_BASE_URL as requested by the deployment architecture
const baseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});


export interface ProcurementRequestCreate {
  material_type: string;
  quantity: number;
  unit: string;
  shipping_deadline: string; // YYYY-MM-DD
  target_country_code: string;
  quality_grade: string;
}

export interface ActiveProcurementRequest {
  id: string;
  status: string;
  material_type: string;
  quantity: number;
  unit: string;
  target_country_code: string;
  quality_grade: string;
  created_at: string;
}

export interface ProcurementRequestCreateResponse {
  request_id: string;
  pipeline_status: string;
  current_agent: string | null;
}

export interface ProcurementStatusResponse {
  request_id: string;
  pipeline_status: string;
  current_agent: string | null;
  supplier_count: number;
  quotation_count: number;
  trust_score_count: number;
  created_at: string;
  completed_at: string | null;
}

export interface RankedSupplier {
  rank: number;
  supplier_id: string;
  supplier_name: string;
  location: string;
  unit_price: number | null;
  currency: string | null;
  scores: Record<string, number>;
}

export interface TrustScoreRow {
  supplier_id: string;
  supplier_name: string | null;
  composite_score: number;
  price_competitiveness: number;
  response_speed_score: number;
  quote_completeness: number;
  referral_score: number;
  computed_at: string;
}

export interface ExtractedQuotationRow {
  quotation_id: string;
  supplier_id: string;
  supplier_name: string | null;
  unit_price: number;
  currency: string;
  moq: number | null;
  delivery_days: number | null;
  validity_days: number | null;
  payment_terms: string | null;
  notes: string | null;
  extraction_confidence: number | null;
  missing_fields: string[];
  created_at: string;
}

export interface ProcurementResultsResponse {
  request_id: string;
  pipeline_status: string;
  ranked_suppliers: RankedSupplier[];
  trust_scores: TrustScoreRow[];
  extracted_quotations: ExtractedQuotationRow[];
  final_recommendation_report: string | null;
  analyst_summary: string | null;
}

export const procurementApi = {
  createRequest: async (data: ProcurementRequestCreate) => {
    try {
      const response = await apiClient.post<ProcurementRequestCreateResponse>('/procurement/request', data);
      return response.data;
    } catch (error) {
      console.error("Failed to create request. The backend might be asleep.", error);
      throw error;
    }
  },
  getStatus: async (id: string) => {
    try {
      const response = await apiClient.get<ProcurementStatusResponse>(`/procurement/${id}/status`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get status for ${id}`, error);
      throw error;
    }
  },
  getResults: async (id: string) => {
    try {
      const response = await apiClient.get<ProcurementResultsResponse>(`/procurement/${id}/results`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get results for ${id}`, error);
      throw error;
    }
  },
  getActive: async () => {
    try {
      const response = await apiClient.get<ActiveProcurementRequest[]>('/procurement/active');
      return response.data;
    } catch (error) {
      console.error('Failed to get active requests', error);
      throw error;
    }
  },
  getMaterials: async () => {
    try {
      const response = await apiClient.get<{ materials: string[] }>('/procurement/materials');
      return response.data;
    } catch (error) {
      console.error('Failed to get materials', error);
      throw error;
    }
  },
};
