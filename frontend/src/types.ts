export type Parsed = { filename:string; headers:string[]; rows:string[][]; warnings:string[]; row_count:number; sample_rows:string[][] };
export type Node = {id:string;name:string;normalized_name:string;entity_type:string;source_file:string;import_id:string};
export type Relationship = {source_id:string;target_id:string;predicate:string;source_file:string;import_id:string};
export type Preview = {nodes:Node[];relationships:Relationship[];primary_nodes:Node[];secondary_nodes:Node[];warnings:string[];summary:Record<string,number>;import_id:string};
