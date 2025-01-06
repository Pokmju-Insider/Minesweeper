```dot
digraph G {
    rankdir=LR;
    "log p_θ(x)" -> "E_q_ϕ[log (p_θ(z,x)/q_ϕ) ]" [label="D_KL(q_ϕ || p_θ)", dir=back];
}
