export type RaffleType = 'express' | 'standard' | 'premium'

export type RaffleStatus = 'active' | 'waiting' | 'drawing' | 'completed' | 'cancelled'

export interface Raffle {
  id: number
  type: RaffleType
  status: RaffleStatus
  min_participants: number
  current_participants: number
  entry_fee_ton: number
  prize_pool_ton: number
  commission_percent: number
  created_at: string
  waiting_until?: string
  drawn_at?: string
  winner_id?: number
  random_org_signature?: string
  random_org_url?: string
}

export interface Participant {
  id: number
  raffle_id: number
  user_id: number
  joined_at: string
  transaction_hash?: string
  is_winner: boolean
  prize_sent: boolean
}

export interface User {
  id: number
  telegram_id: number
  username?: string
  ton_wallet?: string
  total_participations: number
  total_wins: number
  total_spent_ton: number
  total_won_ton: number
  created_at: string
  last_active: string
}

export interface WebSocketMessage {
  type: 'raffle_update' | 'raffle_started' | 'raffle_completed' | 'pong'
  raffle_id?: number
  data?: any
  winner_id?: number
  waiting_until?: string
}
