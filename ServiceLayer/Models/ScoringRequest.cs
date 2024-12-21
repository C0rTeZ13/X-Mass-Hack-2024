namespace ServiceLayer.Models
{
    public class ScoringRequest
    {
        public string INN { get; set; }
        public string? OKVED { get; set; }
        public uint? OKVEDCount { get; set; }  
        public int? EmployeeCount { get; set; }
        public string? TaxationSystem { get; set; }
        public decimal? WithdrawalTurnover { get; set; }
        public decimal? FormWithdrawalTurnover { get; set; }
        public decimal? Revenue { get; set; }
        public uint? ZSK { get; set; }
        public decimal? Scammers { get; set; }
        public decimal? RegistrarServices { get; set; }
        public string? NegativeInformation { get; set; }
        public decimal? TaxBurden { get; set; }
    }
}
