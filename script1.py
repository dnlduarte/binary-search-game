"""
Sistema Bancário
Arquitetura em camadas: Domain → Repository → Service → CLI
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────────
# DOMAIN
# ─────────────────────────────────────────────

class TipoTransacao(Enum):
    DEPOSITO = "DEP"
    SAQUE    = "SAQ"


@dataclass(frozen=True)
class Transacao:
    tipo: TipoTransacao
    valor: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conta:
    id: str
    usuario: str
    _senha_hash: str
    saldo: float = 0.0
    extrato: list[Transacao] = field(default_factory=list)

    # ── fábrica ──────────────────────────────
    @classmethod
    def criar(cls, usuario: str, senha: str) -> "Conta":
        return cls(
            id=str(uuid.uuid4()),
            usuario=usuario,
            _senha_hash=cls._hash(senha),
        )

    # ── autenticação ─────────────────────────
    @staticmethod
    def _hash(senha: str) -> str:
        return hashlib.sha256(senha.encode()).hexdigest()

    def autenticar(self, senha: str) -> bool:
        return self._senha_hash == self._hash(senha)

    # ── operações financeiras ─────────────────
    def depositar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de depósito deve ser positivo.")
        self.saldo += valor
        self.extrato.append(Transacao(TipoTransacao.DEPOSITO, valor))

    def sacar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de saque deve ser positivo.")
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente.")
        self.saldo -= valor
        self.extrato.append(Transacao(TipoTransacao.SAQUE, valor))


# ─────────────────────────────────────────────
# REPOSITORY  (abstração sobre persistência)
# ─────────────────────────────────────────────

class ContaRepository:
    """Em produção: troca por implementação com banco de dados."""

    def __init__(self) -> None:
        self._store: dict[str, Conta] = {}

    def salvar(self, conta: Conta) -> None:
        self._store[conta.usuario] = conta

    def buscar_por_usuario(self, usuario: str) -> Optional[Conta]:
        return self._store.get(usuario)

    def existe(self, usuario: str) -> bool:
        return usuario in self._store


# ─────────────────────────────────────────────
# SERVICE  (casos de uso / regras de negócio)
# ─────────────────────────────────────────────

class BancoService:
    def __init__(self, repo: ContaRepository) -> None:
        self._repo = repo

    def criar_conta(self, usuario: str, senha: str) -> Conta:
        if self._repo.existe(usuario):
            raise ValueError(f"Usuário '{usuario}' já cadastrado.")
        conta = Conta.criar(usuario, senha)
        self._repo.salvar(conta)
        return conta

    def autenticar(self, usuario: str, senha: str) -> Conta:
        conta = self._repo.buscar_por_usuario(usuario)
        if not conta or not conta.autenticar(senha):
            raise PermissionError("Credenciais inválidas.")
        return conta

    def depositar(self, conta: Conta, valor: float) -> None:
        conta.depositar(valor)
        self._repo.salvar(conta)

    def sacar(self, conta: Conta, valor: float) -> None:
        conta.sacar(valor)
        self._repo.salvar(conta)


# ─────────────────────────────────────────────
# CLI  (apresentação — separada da lógica)
# ─────────────────────────────────────────────

def _ler_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  ✗ Valor inválido.")


def _ler_str(prompt: str) -> str:
    valor = input(prompt).strip()
    if not valor:
        raise ValueError("Campo obrigatório.")
    return valor


def _menu_autenticado(service: BancoService, conta: Conta) -> None:
    opcoes = {
        "1": "Depósito",
        "2": "Saque",
        "3": "Saldo",
        "4": "Extrato",
        "0": "Logout",
    }
    while True:
        print("\n" + "─" * 30)
        for k, v in opcoes.items():
            print(f"  {k} · {v}")

        op = input("\n> ").strip()

        if op == "1":
            valor = _ler_float("  Valor: R$ ")
            try:
                service.depositar(conta, valor)
                print(f"  ✓ Depositado R$ {valor:.2f}")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif op == "2":
            valor = _ler_float("  Valor: R$ ")
            try:
                service.sacar(conta, valor)
                print(f"  ✓ Sacado R$ {valor:.2f}")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif op == "3":
            print(f"  Saldo atual: R$ {conta.saldo:.2f}")

        elif op == "4":
            if not conta.extrato:
                print("  Nenhuma transação registrada.")
            for t in conta.extrato:
                sinal = "+" if t.tipo == TipoTransacao.DEPOSITO else "-"
                print(f"  {t.timestamp:%d/%m %H:%M}  {sinal}R$ {t.valor:.2f}")

        elif op == "0":
            print("  Sessão encerrada.")
            break


def main() -> None:
    repo    = ContaRepository()
    service = BancoService(repo)

    print("=" * 30)
    print("      BANCO CLI")
    print("=" * 30)

    while True:
        print("\n  1 · Criar conta")
        print("  2 · Login")
        print("  0 · Sair")

        op = input("\n> ").strip()

        if op == "1":
            try:
                usuario = _ler_str("  Usuário: ")
                senha   = _ler_str("  Senha:   ")
                service.criar_conta(usuario, senha)
                print("  ✓ Conta criada.")
            except ValueError as e:
                print(f"  ✗ {e}")

        elif op == "2":
            try:
                usuario = _ler_str("  Usuário: ")
                senha   = _ler_str("  Senha:   ")
                conta   = service.autenticar(usuario, senha)
                print(f"\n  Bem-vindo, {conta.usuario}.")
                _menu_autenticado(service, conta)
            except (ValueError, PermissionError) as e:
                print(f"  ✗ {e}")

        elif op == "0":
            print("  Até logo.")
            break


if __name__ == "__main__":
    main()