using IronPython.Modules;
using Microsoft.Extensions.Configuration;
using OfficeOpenXml;
using ServiceLayer.Models;
using ServiceLayer.Models.Parsing;
using System.Diagnostics;

namespace ServiceLayer.Services
{
    public class ScoringService
    {
        private readonly VbankcenterParserService _parserService;
        private readonly string _scriptPath;
        private readonly string _pythonPath;
        private readonly string _minMaxPath;
        private readonly string _ocvedPath;
        private readonly string _modelPath;

        public ScoringService(VbankcenterParserService parserService, IConfiguration configuration)
        {
            _parserService = parserService;
            _scriptPath = configuration["ScriptPath"];
            _pythonPath = configuration["PythonPath"];
            _minMaxPath = configuration["MinMaxPath"];
            _ocvedPath = configuration["OcvedPath"];
            _modelPath = configuration["ModelPath"];
        }

        public async Task ComplementCompanyFile(string path)
        {
            var fileInfo = new FileInfo(path);
            using var package = new ExcelPackage(fileInfo);
            var worksheet = package.Workbook.Worksheets[0];
            string INN = worksheet.Cells["A2"].Value.ToString();

            if (INN != null)
            {
                CompanyInfo? info = await _parserService.GetСompanyInfoAsync(INN);
                if (worksheet.Cells["D2"].Value == null) worksheet.Cells["D2"].Value = info?.EmemployeeCount;
                if (worksheet.Cells["B2"].Value == null) worksheet.Cells["B2"].Value = info?.ActivityCode;
                if (worksheet.Cells["H2"].Value == null) worksheet.Cells["H2"].Value = info?.Revenue;
                worksheet.Cells["N1"].Value = "Оценка надежности";
                worksheet.Cells["N2"].Value = info?.ReliabilityRating;
                worksheet.Cells["O1"].Value = "Возможная сумма при 3%";
                worksheet.Cells["O2"].Value = info?.RecommendedDealLimit;
            }
            package.SaveAs(path);
        }

        public async Task ExecuteScoring(string path)
        {
            string arguments = $"\"{_scriptPath}\" \"{path}\" \"{path}\" \"{_minMaxPath}\" \"{_ocvedPath}\" \"{_modelPath}\"";

            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (Process process = Process.Start(startInfo))
            {
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                if (!string.IsNullOrWhiteSpace(error))
                {
                    throw new Exception($"Error in python script: {error}");
                }
            };
        }
    }
}
