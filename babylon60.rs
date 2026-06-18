use std::collections::HashMap;
use std::env;
use std::fs;

fn parse_b60_digit(token: &str) -> i64 {
    if token == "-" {
        return 0;
    }
    let tens = token.chars().filter(|&c| c == '<').count() as i64;
    let ones = token.chars().filter(|&c| c == 'Y' || c == 'v' || c == 'T').count() as i64;
    tens * 10 + ones
}

fn parse_b60_number(b60_str: &str) -> i64 {
    let inner = b60_str.trim_matches(|c| c == '[' || c == ']' || c == ' ');
    if inner.is_empty() {
        return 0;
    }
    let places: Vec<&str> = inner.split_whitespace().collect();
    let mut total = 0;
    let mut power = (places.len() - 1) as u32;
    for p in places {
        let val = parse_b60_digit(p);
        total += val * 60_i64.pow(power);
        if power > 0 {
            power -= 1;
        }
    }
    total
}

fn format_b60(mut val: i64) -> String {
    if val == 0 {
        return "[-]".to_string();
    }
    let mut places = Vec::new();
    while val > 0 {
        places.push(val % 60);
        val /= 60;
    }
    places.reverse();
    
    let mut out = Vec::new();
    for p in places {
        if p == 0 {
            out.push("-".to_string());
        } else {
            let tens = p / 10;
            let ones = p % 10;
            let mut s = String::new();
            for _ in 0..tens { s.push('<'); }
            for _ in 0..ones { s.push('Y'); }
            out.push(s);
        }
    }
    format!("[ {} ]", out.join(" "))
}

fn eval_expr(expr: &str, memory: &HashMap<String, i64>) -> i64 {
    if expr.starts_with('[') {
        parse_b60_number(expr)
    } else {
        *memory.get(expr).unwrap_or(&0)
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <script.b60>", args[0]);
        std::process::exit(1);
    }

    let code = fs::read_to_string(&args[1]).expect("Failed to read script");
    let lines: Vec<&str> = code.lines().map(|l| l.split('#').next().unwrap().trim()).collect();
    
    let mut memory: HashMap<String, i64> = HashMap::new();
    let mut labels: HashMap<String, usize> = HashMap::new();

    for (i, line) in lines.iter().enumerate() {
        if line.starts_with("MUB ") {
            let name = line.split_whitespace().nth(1).unwrap();
            labels.insert(name.to_string(), i);
        }
    }

    let mut pc = 0;
    while pc < lines.len() {
        let line = lines[pc];
        if line.is_empty() || line == "DUB" || line.starts_with("MUB ") {
            pc += 1;
            continue;
        }

        let mut tokens = Vec::new();
        let mut in_bracket = false;
        let mut cur = String::new();
        for c in line.chars() {
            if c == '[' {
                in_bracket = true;
                cur.push(c);
            } else if c == ']' {
                in_bracket = false;
                cur.push(c);
                tokens.push(cur.trim().to_string());
                cur.clear();
            } else if c.is_whitespace() && !in_bracket {
                if !cur.is_empty() {
                    tokens.push(cur.clone());
                    cur.clear();
                }
            } else {
                cur.push(c);
            }
        }
        if !cur.is_empty() {
            tokens.push(cur);
        }

        if tokens.is_empty() {
            pc += 1;
            continue;
        }

        let cmd = tokens[0].as_str();
        match cmd {
            "SAR" => {
                let val = eval_expr(&tokens[1], &memory);
                println!("SAR (DEC): {}", val);
            }
            "SAR.B60" => {
                let val = eval_expr(&tokens[1], &memory);
                println!("SAR (B60): {}", format_b60(val));
            }
            "NIG" => {
                let var = tokens[1].clone();
                let val = eval_expr(&tokens[2], &memory);
                memory.insert(var, val);
            }
            "DAH" => {
                let var = tokens[1].clone();
                let val = eval_expr(&tokens[2], &memory);
                let entry = memory.entry(var).or_insert(0);
                *entry += val;
            }
            "LAL" => {
                let var = tokens[1].clone();
                let val = eval_expr(&tokens[2], &memory);
                let entry = memory.entry(var).or_insert(0);
                *entry -= val;
            }
            "ARA" => {
                let var = tokens[1].clone();
                let val = eval_expr(&tokens[2], &memory);
                let entry = memory.entry(var).or_insert(0);
                *entry *= val;
            }
            "BA" => {
                let var = tokens[1].clone();
                let val = eval_expr(&tokens[2], &memory);
                if val != 0 {
                    let entry = memory.entry(var).or_insert(0);
                    *entry /= val;
                }
            }
            "GIN" => {
                if let Some(&target) = labels.get(&tokens[1]) {
                    pc = target;
                    continue;
                }
            }
            "TUKU" => {
                let val = eval_expr(&tokens[1], &memory);
                if val != 0 {
                    if let Some(&target) = labels.get(&tokens[2]) {
                        pc = target;
                        continue;
                    }
                }
            }
            "NU" => {
                let val = eval_expr(&tokens[1], &memory);
                if val == 0 {
                    if let Some(&target) = labels.get(&tokens[2]) {
                        pc = target;
                        continue;
                    }
                }
            }
            _ => {
                eprintln!("Unknown command: {}", cmd);
            }
        }
        pc += 1;
    }
}
