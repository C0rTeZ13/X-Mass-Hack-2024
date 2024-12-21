using DataLayer;
using DataLayer.Entities;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using ServiceLayer.Constants;
using ServiceLayer.Models.Settings;

namespace ServiceLayer.Services
{
    public class DatabaseInitService : BackgroundService
    {
        private readonly UserManager<AppUser> _userManager;
        private readonly RoleManager<IdentityRole> _roleManager;
        private readonly AppDbContext _dbContext;
        private readonly SuperuserSettings _adminSettings;
        private readonly ILogger<DatabaseInitService> _logger;

        public DatabaseInitService(
            UserManager<AppUser> userManager, 
            RoleManager<IdentityRole> roleManager, 
            AppDbContext dbContext, 
            IOptions<SuperuserSettings> adminSettings,
            ILogger<DatabaseInitService> logger)
        {
            _userManager = userManager;
            _roleManager = roleManager;
            _dbContext = dbContext;
            _adminSettings = adminSettings.Value;
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            try
            {
                await MigrateDatabaseAsync();
                await SeedDatabaseDataAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An error occurred during database initialization.");
                throw;
            }
        }

        private async Task MigrateDatabaseAsync()
        {
            try
            {
                _logger.LogInformation("Migrating database...");
                await _dbContext.Database.MigrateAsync();
                _logger.LogInformation("Database migration completed.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An error occurred during database migration.");
                throw;
            }
        }

        private async Task SeedDatabaseDataAsync()
        {
            try
            {
                // Ensure roles are created
                foreach (var role in AppRoles.AllRoles())
                {
                    IdentityRole? identity_role = await _roleManager.FindByNameAsync(role);
                    if (identity_role == null)
                    {
                        IdentityResult result = await _roleManager.CreateAsync(new IdentityRole(role));
                        if (!result.Succeeded)
                        {
                            _logger.LogError("Failed to create role {Role}", role);
                            throw new Exception($"Failed to create role {role}");
                        }
                    }
                }

                // Ensure superuser exists
                if (string.IsNullOrEmpty(_adminSettings.UserName) || string.IsNullOrEmpty(_adminSettings.Password))
                {
                    throw new ArgumentNullException("SuperuserSettings", "UserName or Password cannot be null or empty.");
                }

                AppUser? adminUser = await _userManager.FindByNameAsync(_adminSettings.UserName);
                if (adminUser == null)
                {
                    adminUser = new AppUser()
                    {
                        UserName = _adminSettings.UserName,
                    };

                    IdentityResult result = await _userManager.CreateAsync(adminUser, _adminSettings.Password);
                    if (!result.Succeeded)
                    {
                        _logger.LogError("Failed to create superuser.");
                        throw new Exception("Failed to create superuser.");
                    }

                    result = await _userManager.AddToRoleAsync(adminUser, AppRoles.Admin);
                    if (!result.Succeeded)
                    {
                        _logger.LogError("Failed to add superuser to role {Role}", AppRoles.Admin);
                        throw new Exception("Failed to add superuser to role.");
                    }

                    _logger.LogInformation("Superuser created successfully.");
                }
                else
                {
                    _logger.LogInformation("Superuser already exists.");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An error occurred during data seeding.");
                throw;
            }
        }
    }
}
