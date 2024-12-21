using ServiceLayer.Services;
using ServiceLayer.Models.Parsing;


namespace Utils
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            VbankcenterParserService parserService = new VbankcenterParserService();
            string text = File.ReadAllText("C://Files/inns.txt");
            string[] INNs = text.Split(Environment.NewLine).ToArray();
            using StreamWriter writer = new("C://Files/parsing.csv");
            writer.WriteLine("INN,Rating,RecommendedDealLimit,Revenue,ActivityCode,EmemployeeCount");
            long count = 0;
            foreach (var inn in INNs[..20_000])
            {
                try
                {
                    CompanyInfo? report = await parserService.GetСompanyInfoAsync(inn);
                    if (report != null)
                    {
                        writer.WriteLine(report);
                    }
                }

                catch (Exception ex) 
                { 
                    Console.WriteLine(ex.ToString());
                }
                count++;
                Console.WriteLine(count);
            }
        }       
    }   
}
