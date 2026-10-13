import type {Parsed,Preview} from './types';
const BASE=import.meta.env.VITE_API_URL||'http://localhost:8001/api';
async function request<T>(path:string, init?:RequestInit):Promise<T>{const r=await fetch(`${BASE}${path}`,init);const body=await r.json();if(!r.ok)throw new Error(body.detail||'Request failed');return body;}
export function parseCsv(file:File){const form=new FormData();form.append('file',file);return request<Parsed>('/csv/parse',{method:'POST',body:form});}
export function preview(payload:unknown){return request<Preview>('/graph/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});}
export function testNeo4j(){return request<{ok:boolean;message:string}>('/neo4j/test');}
export function importGraph(payload:unknown){return request<{ok:boolean;nodes:number;relationships:number}>('/graph/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});}
