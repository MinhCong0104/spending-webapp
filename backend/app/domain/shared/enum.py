from app.shared.utils.general import ExtendedEnum


class UserStatus(str, ExtendedEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class UserRole(str, ExtendedEnum):
    ACCOUNTANT = "accountant"
    USER = "user"
    ADMIN = "admin"


class AuthGrantType(str, ExtendedEnum):
    RESET_PASSWORD = "reset_password"
    ACCESS_TOKEN = "access_token"


class AccountRootType(str, ExtendedEnum):
    ASSETS = "Assets"
    REVENUE = "Revenue"
    EXPENSES = "Expenses"
    EQUITY = "Equity"


class AccountType(str, ExtendedEnum):
    HOLDINGS = "Holdings"
    CASH = "Cash"
    REVENUE = "Revenue"
    EXPENSES = "Expenses"
    SHARE_CAPITAL = "Share Capital"


ACCOUNT_GROUP_MAPPING = {
    AccountType.HOLDINGS: AccountRootType.ASSETS,
    AccountType.CASH: AccountRootType.ASSETS,
    AccountType.REVENUE: AccountRootType.REVENUE,
    AccountType.EXPENSES: AccountRootType.EXPENSES,
    AccountType.SHARE_CAPITAL: AccountRootType.EQUITY,
}


class JournalType(str, ExtendedEnum):
    ICO = "ico"
    LENDING_INCOME = "lending_income"
    MINING = "mining"
    STAKING_INCOME = "staking_income"
    GAS_FEES = "gas_fees"
    MINT = "mint"


class JournalStatus(str, ExtendedEnum):
    DRAFT = "Draft"
    SAVED = "Saved"
    SUBMITTED = "Submitted"
    CANCELLED = "Cancelled"


class BalanceType(str, ExtendedEnum):
    DEBIT = "Debit"
    CREDIT = "Credit"


# JournalType: [AccountType(debit), AccountType(credit)]
JOURNAL_ACCOUNT_MAPPING = {
    JournalType.ICO: [AccountType.HOLDINGS, AccountType.CASH],
    JournalType.LENDING_INCOME: [AccountType.CASH, AccountType.REVENUE],
    JournalType.MINING: [AccountType.CASH, AccountType.REVENUE],
    JournalType.STAKING_INCOME: [AccountType.CASH, AccountType.REVENUE],
    JournalType.GAS_FEES: [AccountType.EXPENSES, AccountType.CASH],
    JournalType.MINT: [AccountType.HOLDINGS, AccountType.CASH],
}

JOURNAL_TYPE_NAME_MAPPING = {
    JournalType.ICO: "ICO",
    JournalType.LENDING_INCOME: "Lending Income",
    JournalType.MINING: "Mining",
    JournalType.STAKING_INCOME: "Staking Income",
    JournalType.GAS_FEES: "Gas fees",
    JournalType.MINT: "Mint",
}


class NumberSeriesType(str, ExtendedEnum):
    Journal = "Journal"
    Transaction = "Transaction"


class LedgerReferenceType(str, ExtendedEnum):
    Journal = "Journal"


class TransactionStatus(str, ExtendedEnum):
    RAW = "raw"
    CLASSIFIED = "classified"


class TransactionType(str, ExtendedEnum):
    RECEIVE = "Receive"
    SEND = "Send"


class Periodicity(str, ExtendedEnum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


class AddressType(str, ExtendedEnum):
    Wallets = "Wallets"
    Exchanges = "Exchanges"
